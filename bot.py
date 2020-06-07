from flask import Flask,request
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import csv
from pymongo import MongoClient
from pyad import *
import pyad
from pyad import adquery
import urllib
from validate import validate_user
from pwd import change_pwd

with open('cred.txt') as f1:
    data=csv.reader(f1,delimiter=',')
    for row in data:
        id=row[0]
        pwd=row[1]
client=MongoClient("mongodb+srv://"+id+":"+urllib.parse.quote(pwd)+"@cluster0-lymvb.mongodb.net/<dbname>?retryWrites=true&w=majority")
db=client['whatsapp_db']
collection=db['whatsapp_db']
c_s=db['block_status']
q=adquery.ADQuery()
apbot=Flask(__name__)
@apbot.route('/sms',methods=['GET','POST'])
def reply():
    block=0
    td=str(datetime.date.today())
    num=request.form.get('From')
    num=num.replace('whatsapp:','')
    msg_text=request.form.get('Body')
    x=collection.find_one({'number':num})
    y=c_s.find_one({'entry':td+'-'+num})
    
    try:
        status=x['status']
        block=int(y['bs'])
    except:
        pass
    if(not(int(block)>2)):
        if(bool(x)==False):
            collection.insert({'number':num,'message':msg_text,'status':'otp'})
            msg=MessagingResponse()
            resp=msg.message("""Welcome to Totaltechnology Helpdesk.
*Please enter the secret code to access the Bot*""")
            return(str(msg))
        else:
            msg=MessagingResponse()
            status_check=collection.find_one({'number':num})
            if(status_check['status']=='otp'):
                if(msg_text=='007'):
                    collection.update_one({'number':num},{"$set":{"message":msg_text,"status":'first'}})
                    resp=msg.message("""your secret code has been verified successfully,please enter any of the below:
*1* for password reset by the system,
*2* for changing password as per your choice,""")
                    return(str(msg))
                else:
                    collection.delete_one({'number':num})
                    resp=msg.message("""your code validation failed ,please try again from the begining""" )
                    return(str(msg))
            if(status=='first'):
                if(msg_text=='1'):
                    resp=msg.message("""reset password by system (auto  generated)""" )
                    resp=msg.message("""please write your user id without any space""" )
                    collection.update_one({'number':num},{"$set":{"message":msg_text,"status":'second_reset'}})
                    return(str(msg))
                if(msg_text=='2'):
                    resp=msg.message("""change password with your own choice""" )
                    resp=msg.message("""please write your user id without any space""" )
                    collection.update_one({'number':num},{"$set":{"message":msg_text,"status":'second_change'}})
                    return(str(msg))
                else:
                    resp=msg.message("""please enter 1 or 2 , you last input was invalid""" )
                    collection.update_one({'number':num},{"$set":{"message":msg_text,"status":'first'}})
                    return(str(msg))
                    
            if(status=='second_reset'):
                resp=msg.message("we will validate the userid you entered: "+ msg_text)
                validation_status=validate_user(q,msg_text,num)            
                print(validation_status)
                if(validation_status[0]=='no account'):
                    resp=msg.message("Your account is invalid" )
                    c_s.update_one({'entry':td+'-'+num},{"$set":{"bs":int(block)+1}},upsert=True)
                    num_try=str(int(block)+1)
                    if(num_try=='3'):
                        resp=msg.message("This was your last attempt you cant not use this bot any more" )
                    else:
                        resp=msg.message("This was your #"+num_try+" attempt" )
                        resp=msg.message("Access will be blocked after 3 rd attempt" )
                        
                if(validation_status[0]=='found'):
                    resp=msg.message("Congratulations your mobile number has been validated against active directory" )
                    resp=msg.message("your password will be reset now" )
                    pwd=change_pwd(msg_text)
                    collection.delete_one({'number':num})
                    try:
                        c_s.delete_one({'entry':td+'-'+num})
                    except Exception as e:
                        print(str(e))
                    resp=msg.message("Your password has been changed successfully")
                    resp=msg.message("Your new password is: "+pwd)
                    resp=msg.message("""Thanks for using our service , have a good day,
*please delete all your chat logs from whatsapp as it contents your credentials.*""")
                
                
                if(validation_status[0]=='not found'):
                    resp=msg.message("Your mobile number does not match with the number in Active directory , please try again." )
                    c_s.update_one({'entry':td+'-'+num},{"$set":{"bs":int(block)+1}},upsert=True)
                    num_try=str(int(block)+1)
                    if(num_try=='3'):
                        resp=msg.message("This was your last attempt you cant not use this bot any more" )
                    else:
                        resp=msg.message("This was your #"+num_try+" attempt" )
                        resp=msg.message("Access will be blocked after 3 rd attempt" )
                               
            return(str(msg))
    else:            
     msg=MessagingResponse()           
     resp=msg.message("Access to this bot has been blocked due to multiple failed attempts" ) 
     return(str(msg))          
    
if __name__=="__main__" :
    apbot.run(port=5002)
    
    
