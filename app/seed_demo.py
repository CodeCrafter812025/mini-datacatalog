# app/seed_demo.py
from app.database import SessionLocal, Base, engine
from app.models import Schema, Table, ETL, DatabaseConnection

def get_or_create(db, model, defaults=None, **kwargs):
    obj = db.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    params = {**(defaults or {}), **kwargs}
    obj = model(**params)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj, True

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # --- نمونه‌های ETL ---
        sales, _ = get_or_create(db, Schema, name="sales")
        orders, _ = get_or_create(db, Table, name="orders", schema_id=sales.id)
        customers, _ = get_or_create(db, Table, name="customers", schema_id=sales.id)

        load_orders, _ = get_or_create(db, ETL, name="load_orders")
        build_customer_dim, _ = get_or_create(db, ETL, name="build_customer_dim")

        if orders not in load_orders.tables:
            load_orders.tables.append(orders)
        if customers not in build_customer_dim.tables:
            build_customer_dim.tables.append(customers)
        db.commit()

        # --- یک اتصال پایگاه داده نمونه ---
        get_or_create(
            db, DatabaseConnection,
            name="local-pg-host",
            host="host.docker.internal",
            port=55432,
            username="admin",
            password="admin123",
            database_name="catalogdb",
            connection_type="postgres",
        )

        print("OK: demo ETLs and one DB connection seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
