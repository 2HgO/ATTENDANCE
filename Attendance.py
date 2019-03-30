#!/home/eseosala/anaconda3/bin/python3
import os,sys
import pickle
import face_recognition as fr
import cv2
from tkinter import Toplevel, Entry, Button, Label, Tk, messagebox
import time
import pymysql

try:
	os.mkdir("Users")
except:
	pass

c=False
user={}
u=sys.argv[1]
p=sys.argv[2]

def disp():
    dd1=[]
    dd2=[]
    for i in os.listdir("Users"):
        da=pickle.load(open("Users/{}".format(i),"rb"))
        dd1.append(da)
        dd2.append(da["Encoding"])
    video_capture= cv2.VideoCapture(0)
    assert video_capture.isOpened()
    proc=True
    t0=time.clock()
    while time.clock()-t0 < 5:
        _, frame=video_capture.read()
        if proc:
            fl=fr.face_locations(frame)
            if len(fl)>0 and proc:    
                fe=fr.face_encodings(frame,num_jitters=10)[0]
                match = fr.compare_faces(dd2,fe,tolerance=0.45)
                if True in match:
                    db=pymysql.connect("localhost",u,p,"AI_4")
                    cursor=db.cursor()
                    state="UPDATE class set Attendance = Attendance+1 where Matric='{}'".format(dd1[match.index(True)]["Matric"])
                    video_capture.release()
                    cursor.execute(state)
                    db.commit()
                    db.close()
                    messagebox.showinfo("Validation","Welcome {}".format(dd1[match.index(True)]["FName"]+" "+dd1[match.index(True)]["LName"]))
                    return
        proc = not proc
    video_capture.release()
    messagebox.showerror("Validation","Could not locate registered student")

def register(a,b,d,top):
    global c
    global user
    a=a.strip()
    b=b.strip()
    d=d.strip()
    if len(a)==0:
        messagebox.showerror("Field Error","Please enter FName!")
        return
    elif len(b)==0:
        messagebox.showerror("Field Error","Please enter LName!")
        return
    elif len(d) != 7:
        messagebox.showerror("Field Error","Please enter valid Matric!")
        return
    c=False
    vid=cv2.VideoCapture(0)
    t=time.clock()
    while time.clock()-t < 12:
        _, frame=vid.read()
        fl=fr.face_locations(frame)
        if len(fl)>0:
            fe = fr.face_encodings(frame,num_jitters=10)[0]
            cv2.rectangle(frame,(fl[0][3],fl[0][0]),(fl[0][1],fl[0][2]),(0,0,255),2)
            cv2.rectangle(frame,(fl[0][3],fl[0][2]-35),(fl[0][1],fl[0][2]),(0,0,255),cv2.FILLED)
            fon=cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame,"is this you? (y/n)",(fl[0][3]+6,fl[0][2]-9),fon,0.5,(255,255,255),1)
            cv2.imshow('video',frame)
            if cv2.waitKey(1) & 0xFF == ord('y'):
                c=True
                dic={}
                dic["FName"]=a
                dic["LName"]=b
                dic["Matric"]=d
                dic["Encoding"]=fe
                user=dic
                cv2.destroyAllWindows()
                vid.release()
                messagebox.showinfo("Validation", "Success")
                return
            elif cv2.waitKey(1) & 0xFF == ord('n'):
                messagebox.showerror("Validation", "Failed")
                break
    cv2.destroyAllWindows()
    vid.release()
    messagebox.showerror("Validation", "Failed")

def vali(top):
    global c
    global user
    if c:
        db=pymysql.connect("localhost",u,p,"AI_4")
        cursor=db.cursor()
        try:
            cursor.execute("INSERT into class(id,Matric,FName,LName,Attendance) VALUE (NULL,'{}','{}','{}',0);".format(user["Matric"],user["FName"],user["LName"]))
            db.commit()
            db.close()
        except:
            db.rollback()
            db.close()
            messagebox.showerror("UserError","Student Already Exists.")
            return
        with open("Users/{}{}.pickle".format(user["FName"],user["LName"]),"wb") as pp:
            pp.write(pickle.dumps(user))
            pp.close()
        messagebox.showinfo("Validation", "Student Registered")
        c=False
        return top.destroy()
    else:
        messagebox.showerror("Validation", "Please record image")


def regi():
    top=Toplevel()
    top.title("Register")
    top.geometry("250x220")
    l1=Label(top,text="FName")
    l1.place(x=10,y=20)
    e1=Entry(top,bd=5)
    e1.place(x=55,y=15)
    l2=Label(top,text="LName")
    l2.place(x=10,y=60)
    e2=Entry(top,bd=5)
    e2.place(x=55,y=55)
    l3=Label(top,text="Matric")
    l3.place(x=10,y=100)
    e3=Entry(top,bd=5)
    e3.place(x=55,y=95)
    rec=Button(top,text="Record Image", command = lambda: register(e1.get(),e2.get(),e3.get(),top))
    rec.place(x=75,y=135)
    reg=Button(top,text="Register",command = lambda:vali(top) )
    reg.place(x=35,y=175)
    can=Button(top,text="Cancel", command=lambda: top.destroy())
    can.place(x=145,y=175)

root=Tk()
root.title("Attendance")
root.geometry("220x200")
log=Button(root,text="Login",command=disp)
r=Button(root,text="Register",command=regi)
log.place(x=30,y=90)
r.place(x=100,y=90)
root.mainloop()
