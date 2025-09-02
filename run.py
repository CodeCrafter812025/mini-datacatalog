# run.py — ساده و واضح
from app import app

if __name__ == "__main__":
    # debug=True برای توسعه و نمایش tracebacks در لاگ
    app.run(host="0.0.0.0", port=5000, debug=True)
