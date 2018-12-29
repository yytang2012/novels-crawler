def get_username_password():
    username_passwords = []
    with open('username_password.txt', encoding="utf8") as f:
        for line in f.readlines():
            segments = line.split(',')
            if len(segments) < 2:
                continue
            username = segments[0].strip()
            password = segments[1].strip()
            username_passwords.append((username, password))
    return username_passwords
