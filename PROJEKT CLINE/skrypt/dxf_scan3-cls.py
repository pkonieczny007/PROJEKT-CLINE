import os 
import fdxf
import time

def scan():
    stan = 1
    x={}
    while stan !='nie':
        dxf_list=[]
        dxf_date=[]
        n=0
        for filename in os.listdir():
            if filename.endswith('.dxf'):
                a={}
                n+=1
                wys=fdxf.wys(filename)
                szer=fdxf.sze(filename)
                date = time.ctime(os.path.getmtime(filename))
                #a = {filename:[wys,szer,date]}
                b = [date,filename,wys,szer]
                #dxf_list.append(a)
                dxf_date.append(b)
                #print(n, filename, wys, szer,date)

        

        dxf_date.sort()
        print(dxf_date[-1])
        stan = input('czy chcesz powtorzyc skanowanie? c -> clear screen ')
        if stan == 'c':
            os.system('cls')
        else:
            continue
    return dxf_list

scan()    

print('dziekuje i zapraszam ponownie;')




           
            
            
