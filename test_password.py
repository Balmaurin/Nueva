import bcrypt

hash = '$2b$12$sSJOJUi2crh4Ae0cYh4NHOsjKfm/ZLZtakw6oRwdKU/Qok394snHe'
password = 'demo123'

if bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8')):
    print('✅ Contraseña correcta')
else:
    print('❌ Contraseña incorrecta')
