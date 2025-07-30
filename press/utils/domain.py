def get_default_domain(subdomain, product_id, fallback_domain):
    """
    Trả về domain mặc định cho site dựa vào product_id.
    Nếu là mbw_cms hoặc go1_cms thì trả về {subdomain}.nhansu360.com
    Ngược lại trả về {subdomain}.{fallback_domain}
    Có thể mở rộng nếu sau này có thêm product_id khác
    """
    if product_id in ("mbw_cms", "go1_cms"):
        return f"{subdomain}.nhansu360.com"
    return f"{subdomain}.{fallback_domain}"