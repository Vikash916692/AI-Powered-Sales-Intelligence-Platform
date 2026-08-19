"""
SQL Security Guardrail and Execution Sandbox.

Enforces strict read-only execution, statement safety, table whitelisting,
SQL injection defense, and query pagination limits.
"""

import re


class SQLSecurityError(Exception):
    """Raised when an unsafe or unauthorized SQL query is detected."""



# Allowed analytical and reporting tables in the warehouse
WHITELISTED_TABLES: set[str] = {
    # Analytical Data Marts (Phase 2)
    "sales_mart",
    "customer_mart",
    "rfm_mart",
    "product_mart",
    "seller_mart",
    "retention_mart",
    "customer_concentration_mart",
    "product_concentration_mart",
    "seller_concentration_mart",
    "delivery_mart",
    "review_mart",
    "sales_intelligence_mart",
    "sales_intelligence_summary",
    "kpi_summary",
    # Intermediate Performance & Cohort Tables
    "customer_performance",
    "product_performance",
    "seller_performance",
    "delivery_performance",
    "customer_rfm",
    "customer_cohort",
    "cohort_size",
    "cohort_retention",
    "cohort_retention_rate",
    "customer_concentration",
    "customer_concentration_summary",
    "product_concentration",
    "product_concentration_summary",
    "seller_concentration",
    "seller_concentration_summary",
    "review_distribution",
    "customer_geography_performance",
    "seller_geography_performance",
    # Star-Schema Facts
    "fact_sales",
    "fact_payments",
    "fact_reviews",
    # Star-Schema Dimensions
    "dim_customer",
    "dim_product",
    "dim_seller",
    "dim_geography",
    "dim_date",
    # Pre-aggregated Tables
    "agg_daily_sales",
    "agg_monthly_sales",
    "agg_product_performance",
    "agg_seller_performance",
    "agg_geography_performance",
    "agg_customer_performance",
}

# Forbidden SQL commands and keywords (case-insensitive)
FORBIDDEN_KEYWORDS: set[str] = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "RENAME",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "CALL",
    "REPLACE",
    "MERGE",
    "LOCK",
    "UNLOCK",
    "FLUSH",
    "SHUTDOWN",
    "INTO OUTFILE",
    "INTO DUMPFILE",
    "LOAD_FILE",
    "LOAD DATA",
    "INFORMATION_SCHEMA",
    "MYSQL",
    "PERFORMANCE_SCHEMA",
    "SYS",
}

DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 1000


class SQLGuard:
    """
    Firewall for LLM-generated SQL queries to ensure safety,
    performance, and warehouse data integrity.
    """

    def __init__(
        self,
        whitelisted_tables: set[str] | None = None,
        default_limit: int = DEFAULT_QUERY_LIMIT,
        max_limit: int = MAX_QUERY_LIMIT,
    ):
        self.whitelisted_tables = whitelisted_tables or WHITELISTED_TABLES
        self.default_limit = default_limit
        self.max_limit = max_limit

    def validate_and_sanitize(self, sql_query: str) -> str:
        """
        Validates the SQL query against security rules and injects safe limits.

        Args:
            sql_query: Raw SQL query string from LLM.

        Returns:
            Sanitized, validated SQL query string ready for execution.

        Raises:
            SQLSecurityError: If any security violation or unsafe pattern is detected.
        """
        if not sql_query or not sql_query.strip():
            raise SQLSecurityError("Empty SQL query received.")

        # 1. Clean markdown code blocks if present
        clean_sql = self._clean_markdown(sql_query)

        # 2. Check for multiple statements / semicolon injection
        self._check_multi_statement(clean_sql)

        # 3. Check for forbidden DDL / DML / Administration commands
        self._check_forbidden_keywords(clean_sql)

        # 4. Verify query is strictly a SELECT or CTE (WITH ... SELECT)
        self._verify_read_only(clean_sql)

        # 5. Verify referenced tables are in whitelist
        self._verify_table_whitelist(clean_sql)

        # 6. Enforce LIMIT clause
        sanitized_sql = self._enforce_limit(clean_sql)

        return sanitized_sql

    def _clean_markdown(self, sql: str) -> str:
        """Strip markdown fences like ```sql ... ```."""
        cleaned = sql.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        return cleaned

    def _check_multi_statement(self, sql: str) -> None:
        """Reject queries containing multiple statements chained by semicolons."""
        # Strip trailing semicolon
        stripped = sql.strip().rstrip(";").strip()
        if ";" in stripped:
            raise SQLSecurityError(
                "Multiple SQL statements detected (semicolon chaining is forbidden)."
            )

    def _check_forbidden_keywords(self, sql: str) -> None:
        """Check for dangerous keywords and administrative commands."""
        # Remove string literals and comments to avoid false positives inside strings
        sql_no_strings = re.sub(r"'[^']*'", "''", sql)
        sql_no_strings = re.sub(r'"[^"]*"', '""', sql_no_strings)
        sql_no_strings = re.sub(r"--.*$", "", sql_no_strings, flags=re.MULTILINE)
        sql_no_strings = re.sub(r"/\*.*?\*/", "", sql_no_strings, flags=re.DOTALL)

        upper_sql = sql_no_strings.upper()

        for kw in FORBIDDEN_KEYWORDS:
            # Match word boundary
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, upper_sql):
                raise SQLSecurityError(
                    f"Forbidden keyword detected in query: '{kw}'. "
                    "Only read-only analytical queries against approved tables are permitted."
                )

    def _verify_read_only(self, sql: str) -> None:
        """Ensure query starts with SELECT or WITH."""
        # Remove comments first
        cleaned = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
        cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL).strip()

        upper_start = cleaned.split()[0].upper() if cleaned.split() else ""
        if upper_start not in {"SELECT", "WITH", "EXPLAIN"}:
            raise SQLSecurityError(
                f"Query must begin with SELECT, WITH, or EXPLAIN. Got: '{upper_start}'"
            )

    def _verify_table_whitelist(self, sql: str) -> None:
        """Extract table names from FROM / JOIN clauses and verify against whitelist."""
        # Normalize sql
        sql_no_strings = re.sub(r"'[^']*'", "''", sql)
        sql_no_strings = re.sub(r'"[^"]*"', '""', sql_no_strings)
        
        # Regex to find FROM and JOIN target tables
        pattern = r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)"
        matches = re.findall(pattern, sql_no_strings, flags=re.IGNORECASE)

        for table in matches:
            t_lower = table.lower()
            # Ignore subqueries or common aliases/keywords
            if t_lower in {"select", "dual", "lateral", "json_table"}:
                continue
            if t_lower not in self.whitelisted_tables:
                raise SQLSecurityError(
                    f"Access to table '{table}' is unauthorized or table does not exist in analytical catalog. "
                    f"Approved tables include: {sorted(self.whitelisted_tables)[:5]}..."
                )

    def _enforce_limit(self, sql: str) -> str:
        """Inject or clamp LIMIT clause to protect memory and client bandwidth."""
        stripped = sql.strip().rstrip(";").strip()

        limit_match = re.search(
            r"\bLIMIT\s+(\d+)(?:\s*,\s*(\d+)|\s+OFFSET\s+(\d+))?\s*$",
            stripped,
            flags=re.IGNORECASE,
        )

        if limit_match:
            requested_limit = int(limit_match.group(1))
            if requested_limit > self.max_limit:
                # Replace with max limit
                start, end = limit_match.span()
                offset_part = ""
                if limit_match.group(2):
                    offset_part = f", {limit_match.group(2)}"
                elif limit_match.group(3):
                    offset_part = f" OFFSET {limit_match.group(3)}"
                stripped = (
                    stripped[:start]
                    + f"LIMIT {self.max_limit}{offset_part}"
                    + stripped[end:]
                )
            return stripped
        else:
            return f"{stripped}\nLIMIT {self.default_limit}"


# Global singleton instance
sql_guard = SQLGuard()
