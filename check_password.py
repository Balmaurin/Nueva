import bcrypt

hash_from_db = '$2b$12$sSJOJUi2crh4Ae0cYh4NHOsjKfm/ZLZtakw6oRwdKU/Qok394snHe'

# Probar posibles contraseñas
passwords = ['demo123', 'demo123456', 'demo', 'password', '123456']

for pwd in passwords:
    if bcrypt.checkpw(pwd.encode('utf-8'), hash_from_db.encode('utf-8')):
        print(f'✅ Contraseña correcta: {pwd}')
        break
else:
    print('❌ Ninguna contraseña común funciona')
