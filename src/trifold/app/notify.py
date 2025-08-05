from sqlalchemy import DDL


# Define the DDL statements
notify_function = DDL(
    """
CREATE OR REPLACE FUNCTION notify_desserts_update() RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('desserts_update', 'changed');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
)

notify_trigger = DDL(
    """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'desserts_notify_trigger'
  ) THEN
    CREATE TRIGGER desserts_notify_trigger
    AFTER INSERT OR UPDATE OR DELETE ON dessert
    FOR EACH ROW EXECUTE FUNCTION notify_desserts_update();
  END IF;
END;
$$;
"""
)
