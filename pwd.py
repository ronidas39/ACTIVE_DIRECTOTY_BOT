import pyad
from pyad import adquery
from password_generator import PasswordGenerator

def change_pwd(msg_text):
    
    q=pyad.adquery.ADQuery()
    q.execute_query(attributes=['distinguishedname','mobile','cn'],where_clause="samaccountname='{}'".format(msg_text))
    x=bool(q.get_results())
    if(str(x)=='True'):
        for row in q.get_results():
            cn=row['distinguishedname']
    aduser=pyad.aduser.ADUser.from_dn(cn)
    pwo= PasswordGenerator()
    pwd='Tt' +pwo.generate()
    pyad.aduser.ADUser.set_password(aduser,pwd)
    return(pwd)
           