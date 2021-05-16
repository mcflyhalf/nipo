from nipo.db import schema

# Kept here to avoid circular import issues
# REally belongs in nipo.db.utils
def get_tables_metadata():
	sorted_tables = schema.Base.metadata.sorted_tables

	return sorted_tables