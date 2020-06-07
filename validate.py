from pyad import adquery
import pyad
import pythoncom

def validate_user(q,msg_text,num):
    pythoncom.CoInitialize()
    try:
        q.execute_query(attributes=['distinguishedname','mobile','cn'],where_clause="samaccountname='{}'".format(msg_text))
    except Exception as e:
        print(str(e))
    x=bool(q.get_results())
    l=[]
    if(q.get_row_count()==1):
        for row in q.get_results():
            mob=row['mobile']
            cn=row['cn']
            if(mob==num):
                l.append('found')
                l.append(cn)
                return(l)
                
                
            else:
                l.append('not found')
                l.append(cn)
                return(l)
                                   
    else:
        l.append('no account')
        l.append('no cn')            
        return(l)  