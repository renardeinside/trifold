from sqlalchemy import DDL
from enum import Enum
from pydantic import BaseModel
from trifold.app.models import CamelModel, Dessert, DessertOut

NOTIFY_CHANNEL = "desserts_update"

# Define the DDL statements
notify_function = DDL(
    f"""
DO $$
BEGIN
  -- Check if function exists, create only if it doesn't
  BEGIN
    PERFORM 'public.notify_desserts_update()'::regprocedure;
  EXCEPTION WHEN undefined_function THEN
    CREATE FUNCTION notify_desserts_update() RETURNS trigger AS $func$
    DECLARE
      payload json;
    BEGIN
      -- For DELETE operations, use OLD record; for INSERT/UPDATE use NEW record
      IF TG_OP = 'DELETE' THEN
        payload = json_build_object(
          'operation', TG_OP,
          'table', TG_TABLE_NAME,
          'data', row_to_json(OLD)
        );
        PERFORM pg_notify('{NOTIFY_CHANNEL}', payload::text);
        RETURN OLD;
      ELSE
        payload = json_build_object(
          'operation', TG_OP,
          'table', TG_TABLE_NAME,
          'data', row_to_json(NEW)
        );
        PERFORM pg_notify('{NOTIFY_CHANNEL}', payload::text);
        RETURN NEW;
      END IF;
    END;
    $func$ LANGUAGE plpgsql;
  END;
END
$$;
"""
)

notify_trigger = DDL(
    """
DO $$
BEGIN
  -- Check if trigger exists, create only if it doesn't
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgname = 'desserts_notify_trigger'
  ) THEN
    CREATE TRIGGER desserts_notify_trigger
    AFTER INSERT OR UPDATE OR DELETE ON dessert
    FOR EACH ROW EXECUTE FUNCTION notify_desserts_update();
  END IF;
END
$$;
"""
)


class OperationType(str, Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class NotificationOut(CamelModel):
    operation: OperationType
    data: DessertOut


class Notification(BaseModel):
    operation: OperationType
    data: Dessert

    def to_out(self) -> NotificationOut:
        return NotificationOut(
            operation=self.operation, data=DessertOut.from_model(self.data)
        )
