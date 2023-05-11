def format_phone_num(pn: str) -> str:
    return f"+{pn[:3]}({pn[3:5]}){pn[5:8]}-{pn[8:10]}-{pn[10:]}"


def sanitize_phone_num(pn: str) -> str:
    tel_code = {9: "380", 10: "38"}
    snz_phone = "".join([ch for ch in pn if ch.isdecimal()])
    if len(snz_phone) not in (9, 10, 12):
        raise ValueError(f"Phone '{pn}' is incorrect.")
    return tel_code.get(len(snz_phone), "") + snz_phone


if __name__ == '__main__':
    p_num = "0445421245"
    print(format_phone_num(sanitize_phone_num(p_num)))
