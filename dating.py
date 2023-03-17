#coding=utf-8
from chatgpt_interface import get_g3t_response,hybirdsplit,keyword_fix
from params_helper import load_prompts,load_aips
import uuid
import sys
import os
import pprint
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--apikey', type=str,help='api-key')
args = parser.parse_args()
apikey=args.apikey



class script():
    def __init__(self,actor,acname,before,content):
        self.actor = actor  # ai user nar 
        self.acname = acname
        self.before = before
        self.content = acname+"："+content
        
class ai_partner():
    def __init__(self,api_key):
        self.api_key = api_key 
        self.name = ""
        self.image = ""
        self.character = ""
        self.sexpre = ""
        self.keyword = None
    def get_name(self,name):
        self.name = name 
    def get_image(self,pdict):
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":pdict['pimage'].replace('【name】',self.name)}
            ]
        self.image = get_g3t_response(messages,self.api_key,hh=1).strip()
    def get_character(self,pdict):
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":pdict['pcharacter'].replace('【name】',self.name)}
            ]
        self.character = get_g3t_response(messages,self.api_key,hh=1).strip()
    def get_aip_sexual_preference(self,pdict):
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":pdict['psexpre'].replace('【name】',self.name).replace('【character】',self.character)}
            ]
        self.sexpre = hybirdsplit(get_g3t_response(messages,self.api_key))
    def load_aip_bydict(self,daip,i):
        #从字典里读取aip
        self.name = daip['name'][i]
        self.image = daip['image'][i]
        self.character = daip['character'][i]
        self.sexpre = daip['sexpre'][i]
        self.keyword = daip['keyword'][i]
    
    def create_aip_by_kws(self,text,pdict):
        imagekw = text.split('[imagekw]')[1].split('[/imagekw]')[0]
        characterkw = text.split('[characterkw]')[1].split('[/characterkw]')[0]
        sexprekw = text.split('[sexprekw]')[1].split('[/sexprekw]')[0]
        self.keyword = text.split('[keyword]')[1].split('[/keyword]')[0]
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":pdict['pimagekw'].replace('【name】',self.name).replace('【imagekw】',imagekw)}
            ]
        self.image = get_g3t_response(messages,self.api_key,hh=1).strip()
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":pdict['pcharacterkw'].replace('【name】',self.name).replace('【characterkw】',characterkw)}
            ]
        self.character = get_g3t_response(messages,self.api_key,hh=1).strip()
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":pdict['psexprekw'].replace('【name】',self.name).replace('【character】',self.character).replace('【sexprekw】',sexprekw)}
            ]
        self.sexpre = hybirdsplit(get_g3t_response(messages,self.api_key))
        return 0

    def create_aip(self,text):
        self.name = text.split('[name]')[1].split('[/name]')[0]
        self.image = text.split('[image]')[1].split('[/image]')[0]
        self.character = text.split('[character]')[1].split('[/character]')[0]
        self.sexpre = text.split('[sexpre]')[1].split('[/sexpre]')[0]
        self.keyword = text.split('[keyword]')[1].split('[/keyword]')[0]

    def create_aip2(self,text,pdict):
        self.name = text.split('[name]')[1].split('[/name]')[0]
        self.create_aip_by_kws(self,text,pdict)
        return 0

class aicrush():
    def __init__(self,api_key,uid):
        self.api_key  = api_key
        self.uid = uid 
        self.debug = 0 
        self.aip = None
        self.scripts = []
        self.mainline = []
        self.now = -3 
        self.piv = 0
        self.history = []
        self.period = 0
        self.get_dicts()
        self.accinp = 0
        self.uact = ''
        self.tmpact = ' '
        self.idxerror = 0
        self.keyword = ''
        self.init_prompt = ''
    def get_dicts(self):
        self.pdict,self.dcode0,self.dcode1,self.dcodesp,self.lcode0,self.lcode1,self.lcodesp = load_prompts()
        self.aipdict = load_aips()

    def add_script(self,ns):
        self.scripts.append(ns)
        self.history.append('0')
        return len(self.scripts)-1,str(len(self.scripts)-1)+" "+ns.content

    def get_history(self):
        # history = 上一个的总结+这次的对话
        b = self.scripts[self.now].before
        count = 0
        if b == -1:
            self.get_history_now()
            return self.history[0]
        else:
            self.get_history_now()
            a = self.now
            count = 0
            while(count == 0):
                if self.scripts[a].actor != 'nar':
                    count = count + 1 
                else:
                    a = self.scripts[a].before
            if self.idxerror > 2:
                s = self.scripts[a].content
                s1 = s[:len(s)]
                s2 = s[len(s)//2:]
                s1.replace('.','。').replace(')','）').replace(']','】')
                s11 = s1.split('。',1)[1]
                s12 = s1.split('】',1)[1]
                s13 = s1.split('）',1)[1]
                s1n = min([s11,s12,s13], key=len)
                tmp = self.history[self.now] + s1n+s2
            else:
                tmp = self.history[self.now] + self.scripts[a].content
            #print(tmp)
            return  tmp
    def get_history_now(self):
        a = self.now
        if self.history[self.now]=='0':
            if a == 0:
                history = self.aip.sexpre + self.scripts[a].content 
                messages=[
                    {"role": "system", "content": ""},
                    {'role': "user", "content":self.pdict['phistory'].replace("【history】",history)}
                    ]
                tmp = get_g3t_response(messages,self.api_key)
                #print(tmp)
                self.history[self.now]=tmp 
            else:
                count = 0
                history = ""
                while(count == 0):
                    b = self.scripts[a].before
                    if self.scripts[a].actor != 'nar':
                        history = self.history[b] + self.scripts[a].content
                        count = count + 1 
                    a = self.scripts[a].before

                messages=[
                    {"role": "system", "content": ""},
                    {'role': "user", "content":self.pdict['phistory'].replace("【history】",history)}
                    ]
                tmp = get_g3t_response(messages,self.api_key)
                #print(tmp)
                self.history[self.now]=tmp
    def first_sight(self):
        self.accinp = 0
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['penvinit'].replace('【initprompt】',self.init_prompt).replace("【name】",self.aip.name).replace("【image】",self.aip.image.replace('\n',"，"))}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        new_sc = script('nar',"旁白",-1,tmp)
        self.now,content = self.add_script(new_sc)
        self.accinp = 0
        return content

    def say_hello(self):
        #history = self.get_history()
        self.accinp = 0
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['phello'].replace('【initprompt】',self.init_prompt).replace("【name】",self.aip.name).replace("【sexpre】",self.aip.sexpre.replace('\n',"，")).replace("【history】",self.get_history()).replace('【keywords】',self.keyword)}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        new_sc = script('ai',self.aip.name,self.now,tmp)
        self.now,content = self.add_script(new_sc)
        self.accinp = 0
        return content
    def ai_action_auto(self):
        # period 2 
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['pautodiag'].replace("【name】",self.aip.name).replace("【history】",self.get_history())}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        self.tmpact = tmp
        content = ("自动回复："+tmp+'\n 确定y，重写r，取消n。')
        self.period = 3
        self.accinp = 1 
        return content
    def confirm_auto_act(self,x):
        #period 3  
        if x =='y':
            new_sc = script('user',"男主角",self.now,self.tmpact)
            self.now,content = self.add_script(new_sc)
            self.period = 0
            self.accinp = 0 
            return content
        elif x == 'r':
            self.period = 2 
            self.accinp = 0
            self.tmpact = ''
            return '重新自动生成'
        elif x == 'n':
            self.period = 0
            self.accinp = 0
            return '返回'
        else:
            self.period = 3
            self.accinp = 1
            return '请正确输入'
    def ai_action_byact(self):
        # period 4 
        if self.now == self.uact[0]:
            act  =self.uact[1]
        else:
            self.period = 0
            self.accinp = 0
            return '动作错误，返回'
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['phautodiag'].replace("【name】",self.aip.name).replace("【history】",self.get_history()).replace('【action】',act)}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        self.tmpact = tmp
        content = ("自动回复："+tmp+'\n 确定y，重写r，取消n。')
        self.period = 5
        self.accinp = 1 
        return content

    def confirm_ha_act(self,x):
        #period 5  
        if x =='y':
            new_sc = script('user',"男主角",self.now,self.tmpact)
            self.now,content = self.add_script(new_sc)
            self.period = 0
            self.accinp = 0 
            return content
        elif x == 'r':
            self.period = 4 
            self.accinp = 0
            self.tmpact = ''
            return '重新自动生成'
        elif x == 'n':
            self.period = 0
            self.accinp = 0
            return '返回'
        else:
            self.period = 5
            self.accinp = 1
            return '请正确输入'

    def pre_action(self):
        # period 0 
        self.accinp = 0
        content = "piv:"+str(self.piv)+"。 输入a自动回复，也可以输入c+动作代码,如c34，h查看帮助: "
        self.period = 1 
        self.accinp = 1 
        return content

    def your_action(self,x):
        # period 1 
        self.accinp = 0
        if x == 'a':
            content = "自动回复中……"
            self.period = 2 
        elif x[0]=='c':
            act = self.get_action(x)
            if act == '0':
                self.period = 1 
                self.accinp = 1 
                return '错误的动作代码'
            self.uact = [self.now,act]
            content = act
            self.period = 4 
        elif x[0:2] == 'aa':
            act  = x[2:]
            self.uact = [self.now,act]
            content = act
            self.period = 4 
            #tmp = self.ai_action_byact(x[2:])
        elif x[0] == 'w':
            content = x[1:]
            new_sc = script('user',"男主角",self.now,content)
            self.now,content = self.add_script(new_sc)
            self.period = 0 
        elif x[0] == 'b':
            try:
                if int(x[1:]) >= -1:
                    self.now = int(x[1:])
                    content = '回溯到： '+str(self.now)
                    self.period = 0
                else:
                    content = '请正确输入要回溯的对话序号'
            except Exception as e:
                print(e)
                content = '请正确输入要回溯的对话序号'
        elif x == 'e':
            content = '增加一段旁白描写'
            self.period = 6
        elif x == 'p':
            if self.piv == 1:
                self.piv = 0 
                content = '设置为拔出状态'
            else:
                self.piv = 1 
                content = '设置为插入状态'
            self.period = 0 
        elif x =='q':
            self.period = 10
            content = '故事结局'
        elif x=='h':
            content = "帮助：\na：自动回复\naa+动作如“aa男主角搓揉着自己的阳具”\nw+回复直接回复\nc+动作代码,代码表：\n数字代码要输入两位，如c34：抚摸女主角的胸部\n第一位代码："+str(self.dcode0)+'\n第二位代码：'+str(self.dcode1)+'\n特殊代码使用hc0-hc5查看：'+"hc0:普通代码表，hc1：性交动作表，hc2：男m备忘录，hc3：男s备忘录，hc4：脑洞系，hc5后庭系"+"\n b+数字，回溯到之前的对话\np切换插入状态(改变piv值，piv值用来指示插入状态)\ne添加一段旁白\nq为故事写一个结局并退出"
            self.period = 0 
        elif x=='hc0':
            content = "普通代码表：\n" + pprint.pformat(self.pdict['daction']['dcs0'])
            self.period = 0
        elif x=='hc1':
            content = "性交动作表：\n" + pprint.pformat(self.pdict['daction']['dcs1'])
            self.period = 0
        elif x=='hc2':
            content = "男m备忘录：\n" + pprint.pformat(self.pdict['daction']['dcs2'])
            self.period = 0
        elif x=='hc3':
            content = "男s备忘录：\n" + pprint.pformat(self.pdict['daction']['dcs3'])
            self.period = 0
        elif x=='hc4':
            content = "脑洞系：\n" + pprint.pformat(self.pdict['daction']['dcs4'])
            self.period = 0
        elif x=='hc5':
            content = "后庭系：\n" + pprint.pformat(self.pdict['daction']['dcs5'])
            self.period = 0
        else:
            content  = '请正确输入'
            self.period = 0
        return content

    def get_action(self,code):
        if code[0]=='c':
            act = "男主角"
            if code[1:] in self.lcodesp:
                act = act + self.dcodesp[code[1:]].replace('【name】',self.aip.name)
                if code[1:]=='cr':
                    self.piv=1
                if code[1:]=='bc':
                    self.piv=0
                return act
            if self.piv == 1:
                act = act + "一边抽插一边" 
            if code[1] in self.lcode0:
                act = act + self.dcode0[code[1]] +self.aip.name
                if code[2] in self.lcode1:
                    act = act + self.dcode1[code[2]]
                else:
                    return '0'
            else:
                return '0'
        return act

    
            

    def auto_nar(self):
        # period 6 
        self.accinp = 0
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['pautonar'].replace("【name】",self.aip.name).replace("【history】",self.get_history())}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        new_sc = script('nar',"旁白",self.now,tmp)
        self.now,content = self.add_script(new_sc)
        self.accinp = 0
        self.period = 0 
        return content 


    def aip_action(self):
        self.accinp = 0
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['paipact'].replace("【name】",self.aip.name).replace("【history】",self.get_history()).replace('【keywords】',self.keyword)}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        new_sc = script('ai',self.aip.name,self.now,tmp)
        self.now,content = self.add_script(new_sc)
        self.accinp = 0
        return content



    def endding(self):
        #period 10 
        self.accinp = 0
        messages=[
            {"role": "system", "content": ""},
            {'role': "user", "content":self.pdict['pendding'].replace("【history】",self.get_history())}
            ]
        tmp = hybirdsplit(get_g3t_response(messages,self.api_key))
        new_sc,content = script('nar',"结尾",self.now,tmp)
        self.now = self.add_script(new_sc)
        self.accinp = 0
        return content

    def save(self):
        self.mainline = []
        a = self.now
        while(a>=0):
            self.mainline.append(a)
            a = self.scripts[a].before
        self.mainline.reverse()

        filename = uuid.uuid4().hex
        f = open(str(filename)+'.txt', 'w',encoding= 'utf-8')
        f.write("姓名："+self.aip.name+'\n')
        f.write(self.aip.image+'\n')
        f.write(self.aip.character+'\n')
        f.write(self.aip.sexpre+'\n')
        for i in self.mainline:
            f.write(self.scripts[i].content+'\n')
        f.close()
        return "saved"


    def scheduler(self,input):
        try:
            if self.now == -3:
                return self.helloworld()
            if self.now == -2:
                # 0 菜单 - 1 选人 - 2 确定随机人物（random only） -3 确定人物性格
                if self.period == 0 :
                    return self.find_aip()
                if self.period =='start':
                    return self.choice_ai_partner(input)
                if self.period =='raip':
                    return self.choice_random_aip(input)
                if self.period =='kw_raip':
                    return self.halfauto_random_aip(input)
                if self.period =='cfm_raip':
                    return self.confirm_random_aip(input)
                if self.period =='get_kw':
                    return self.get_keyword()
                if self.period =='cfm_kw':
                    return self.confirm_kw(input)
                if self.period == 'usr_aip_full':
                    return self.user_aip(input)
                if self.period == 'usr_aip_kw':
                    return self.user_aip_kw(input)
                if self.period == 'cfm_laip':
                    return self.confirm_aip(input)
                if self.period == 'scene':
                    return self.show_scene()
                if self.period =='cfm_scene':
                    return self.confirm_scene(input)
            if self.now == -1 :
                return self.first_sight()
            else:
                self.mainline = []
                a = self.now
                while(a>=0):
                    self.mainline.append(a)
                    a = self.scripts[a].before
                if len(self.mainline)==1:
                    return self.say_hello()
            a = self.now
            while (self.scripts[a].actor =='nar'):
                a =  self.scripts[a].before
            if self.scripts[a].actor == 'ai':  # ai说完话了该user说了
                if self.period == 0:
                    return self.pre_action()
                if self.period == 1:
                    return self.your_action(input)
                if self.period == 2:
                    return self.ai_action_auto()
                if self.period == 3:
                    return self.confirm_auto_act(input)
                if self.period == 4:
                    return self.ai_action_byact()
                if self.period == 5:
                    return self.confirm_ha_act(input)
                if self.period == 6:
                    return self.auto_nar() 
                if self.period == 10:
                    return self.endding()
            if self.scripts[a].actor == 'user':
                return self.aip_action()
        
        except Exception as e:
            print(e)
            self.idxerror = self.idxerror + 1 
           
    def find_aip(self):
        # period 0 
        self.period = 'start' 
        self.accinp = 1
        return '请选择您的ai伴侣：\n r随机生成伴侣，l+数字在伴侣表中选择，ll查看ai伴侣表，k根据关键词生成ai伴侣，i手动输入ai伴侣。 \n >'
    
    def choice_ai_partner(self,input):
        # period 'start'  
        self.accinp = 0
        if input == 'r':
            self.period = 'raip'
            self.accinp = 0
            return self.random_aip()
        elif input == 'll':
            self.accinp = 0
            content = ""
            for i in range(len(self.aipdict['name'])):
                content = content + str(i)+'.'+self.aipdict['name'][i]+'  '
            content = content + '\n请挑选你中意的伴侣，l+数字在伴侣表中选择：\n >'
            self.accinp = 1
            return content
        elif input[0] == 'l':
            self.accinp = 0
            try:
                x = int(input[1:])
                name  = self.aipdict['name'][x]
                self.aip  = ai_partner(self.api_key)
                self.aip.load_aip_bydict(self.aipdict,x)
                content = ''
                content = content + "姓名："+self.aip.name + '\n'
                content = content +self.aip.image + '\n'
                content = content +self.aip.character + '\n'
                content = content +self.aip.sexpre + '\n'
                content = content + "确定伴侣请输入y，取消请输入n。\n >"
                self.period = 'cfm_laip'
                self.accinp = 1  
                return content
            except:
                content = '请输入正确的编号！'
                self.accinp = 1
                return content
        elif input == 'k':
            self.accinp = 0
            content = '请按照以下格式输入你喜爱的ai设定：\n'
            content = content + '[name]姓名[/name][imagekw]外貌关键词[/imagekw][characterkw]性格关键词[/characterkw][sexprekw]性癖关键词[/sexprekw][keyword]人物关键词[/keyword]'  +"\n输入r返回"
            self.period = "usr_aip_kw" 
            self.accinp = 1
            return content
        elif input == 'i':
            self.accinp = 0
            content = '请按照以下格式输入你喜爱的ai设定：\n'
            content = content + '[name]姓名[/name][image]外貌[/image][character]性格[/character][sexpre]性癖[/sexpre][keyword]关键词[/keyword]' +"\n输入r返回"
            self.period = "usr_aip_full" 
            self.accinp = 1
            return content
        else:
            self.accinp = 1
            return "请输入正确的代码！"

    def helloworld(self):
        self.accinp = 0
        self.now = self.now + 1 
        self.accinp = 0
        return self.pdict['welcome']


    def random_aip(self):
        #随机aip名字
        self.namelist = []
        messages=[
                {"role": "system", "content": ""},
                {'role': "user", "content":self.pdict['pname1']}
                ]
        tmp = get_g3t_response(messages,self.api_key,hh=1)
        for i in tmp.splitlines():
            try:
                
                if i.count('(') ==0 and i.count('（')==0:
                    self.namelist.append(i.split('：')[1])                
                if i.count('(') !=0:
                    self.namelist.append(i.split('：')[1].split('(')[0])
                if i.count('（')!=0:
                    self.namelist.append(i.split('：')[1].split('（')[0])
            except:
                pass
        messages=[
                {"role": "system", "content": ""},
                {'role': "user", "content":self.pdict['pname2']}
                ]
        tmp = get_g3t_response(messages,self.api_key,hh=1)
        for i in tmp.splitlines():
            try:
                if i.count('(') ==0 and i.count('（')==0:
                    self.namelist.append(i.split('：')[1])                
                if i.count('(') !=0:
                    self.namelist.append(i.split('：')[1].split('(')[0])
                if i.count('（')!=0:
                    self.namelist.append(i.split('：')[1].split('（')[0])
            except:
                pass
        content = ""
        for i in range(len(self.namelist)):
            content = content + str(i)+'.'+self.namelist[i]+'  '
        content = content + '\n输入序号挑选你中意的伴侣（AI随机性格）重新寻找请输入r：\n >' 
        self.accinp = 1       
        return content


    def choice_random_aip(self,input):
        #period 'raip' 
        self.accinp = 0 
        try:
            if input=='r':
                self.period = 0
                self.accinp = 0 
                return '返回上一级'
            elif input[0]=='a':
                x = int(input[1:])
                name = self.namelist[x]
                self.aip = ai_partner(self.api_key)
                self.aip.get_name(name)
                content = "请为"+name+"设计性格。\n"+r"按照如下格式：[imagekw]外貌关键词[/imagekw][characterkw]性格关键词[/characterkw][sexprekw]性癖关键词[/sexprekw][keyword]人物关键词[/keyword]"+"\n输入r返回"
                self.period = 'kw_raip' 
                self.accinp = 1 
                return content
            elif input.isdigit():
                content = ''
                x = int(input) 
                name = self.namelist[x]
                self.aip = ai_partner(self.api_key)
                content = content + "你选择了：" + name + '\n'
                self.aip.get_name(name)
                self.aip.get_image(self.pdict)
                self.aip.get_character(self.pdict)
                self.aip.get_aip_sexual_preference(self.pdict)
                content = content + "姓名："+self.aip.name + '\n'
                content = content +self.aip.image + '\n'
                content = content +self.aip.character + '\n'
                content = content +self.aip.sexpre + '\n'
                content = content + "确定伴侣请输入y，取消请输入n。\n >"
                self.period = 'cfm_raip' 
                self.accinp = 1 
                return content
            else:
                self.accinp = 1 
                return '请正确输入！\n' + self.confirm_random_aip('n')
        except:
                self.period = 'raip'
                self.accinp = 1 
                return '请输入正确的编号！\n' + self.confirm_random_aip('n')

    def halfauto_random_aip(self,input):
        self.accinp = 0
        # period 'kw_raip' 
        if input == 'r':
            content = ""
            for i in range(len(self.namelist)):
                content = content + str(i)+'.'+self.namelist[i]+'  '
            content = content + '\n请挑选你中意的伴侣，重新寻找请输入r：\n >' 
            self.period = 'raip' 
            self.accinp = 1
            return content  
        else:
            try:
                content = ""
                self.aip.create_aip_by_kws(input,self.pdict)
                content = content + "姓名："+self.aip.name + '\n'
                content = content +self.aip.image + '\n'
                content = content +self.aip.character + '\n'
                content = content +self.aip.sexpre + '\n'
                content = content + "确定伴侣请输入y，取消请输入n。\n >"
                self.period = 'cfm_raip' 
                self.accinp = 1 
                return content
            except Exception as e:
                print(e)
                self.accinp = 1 
                return '请正确输入！'

    def confirm_random_aip(self,input):
        self.accinp = 0
        # period 'cfm_raip' 
        if input=='y':
            if self.aip.keyword is not None:
                content = '确定选择'+self.aip.name +"。\n当前人物关键词：{}。\n确认请回复y，修改请回复k+关键词（如k傲娇，巨乳），不使用关键词请回复n".format(self.aip.keyword)
                self.period = 'cfm_kw'
                self.accinp = 1
                return content
            else:
                content = '确定选择'+self.aip.name +"。\n请选择人物关键词……"
                self.period = 'get_kw'
                return content
        elif input =='n':
            content = ""
            for i in range(len(self.namelist)):
                content = content + str(i)+'.'+self.namelist[i]+'  '
            content = content + '\n输入序号挑选你中意的伴侣（AI随机性格），重新寻找请输入r：\n >'
            self.period = 'raip' 
            self.accinp = 1
            return content 
        else:
            content = '请正确输入' +'\n'    
            return content

    def user_aip(self,input):
        # period "usr_aip_full"
        if input == 'r':
            self.accinp = 0
            self.period = 0
            content = '返回'
            return content
        else:
            self.accinp = 0
            try:
                self.aip = ai_partner(self.api_key)
                self.aip.create_aip(input)
                content = content + "你选择了：" + name + '\n'
                content = content + "姓名："+self.aip.name + '\n'
                content = content +self.aip.image + '\n'
                content = content +self.aip.character + '\n'
                content = content +self.aip.sexpre + '\n'
                content = content + "确定伴侣请输入y，取消请输入n。\n >"
                self.period = 'cfm_laip'  
            except:
                content = '请按照规则正确输入,返回请输入r'
            self.accinp = 1 
            return content

    def user_aip_kw(self,input):
        # period "usr_aip_kw"
        if input == 'r':
            self.accinp = 0
            self.period = 0
            content = '返回'
            return content
        else:
            self.accinp = 0
            try:
                self.aip = ai_partner(self.api_key)
                self.aip.create_aip2(input)
                content = content + "你选择了：" + name + '\n'
                content = content + "姓名："+self.aip.name + '\n'
                content = content +self.aip.image + '\n'
                content = content +self.aip.character + '\n'
                content = content +self.aip.sexpre + '\n'
                content = content + "确定伴侣请输入y，取消请输入n。\n >"
                self.period = 'cfm_laip' 
            except:
                content = '请按照规则正确输入,返回请输入r'
            self.accinp = 1 
            return content

    def confirm_aip(self,input):
        # period 'cfm_laip'
        self.accinp = 0
        if input=='y':
            if self.aip.keyword is not None:
                content = '确定选择'+self.aip.name +"。\n当前人物关键词：{}".format(self.aip.keyword)
                self.period = 'scene'
                self.accinp = 0
                return content
            else:
                content = '确定选择'+self.aip.name +"。\n请选择人物关键词……"
                self.period = 'get_kw'
                self.accinp = 1
                return content
        elif input =='n':
            content = "返回。"
            self.period = 0
            self.accinp = 0    
            return content
        else:
            content = '请正确输入' +'\n' 
            self.accinp = 1    
            return content

    def get_keyword(self):
        #period ='get_kw'
        self.accinp = 0
        content = "请手动为{}选择一些关键词，来提升剧本生成的性能，根据以下列表选取2-3个，如回复“1 4 9”代表关键词为御姐、女王、掌控男人。也可以使用k+关键词如“k御姐，温柔”来手动指定，不使用关键词请回复n。\n关键词列表：\n".format(self.aip.name)
        for i in range(len(self.pdict['lkws'])):
                content = content + str(i)+'.'+self.pdict['lkws'][i]+' '
        self.period = 'cfm_kw'
        self.accinp = 1 
        return content 
    
    def confirm_kw(self,input):
        #period 'cfm_kw' 
        self.accinp = 0
        try:
            if input[0] == 'n':
                content = "不使用关键词。" 
                self.keyword = ""
                self.period = 'scene'
                self.accinp = 0 
                return content
            elif input[0] == 'k':
                self.aip.keyword =input[1:]
                content = '确定{}使用关键词{}。'.format(self.aip.name,self.aip.keyword)
                self.keyword = '和关键词“{}”'.format(self.aip.keyword)
                self.period = 'scene'
                self.accinp = 0 
                return content
            else:
                kwds = []
                k = input.split()
                for i in k:
                    kwds.append(self.pdict['lkws'][int(i)])
            
                self.aip.keyword ='，'.join(kwds)
                content = '确定{}使用关键词{}。'.format(self.aip.name,self.aip.keyword)
                self.keyword = '和关键词“{}”'.format(self.aip.keyword)
                self.period = 'scene'
                self.accinp = 0 
                return content
        except:
            content = "请正确输入"
            self.period = 'get_kw'
            self.accinp = 0
            return content
        


    def show_scene(self):
        # period scene
        content = '可以选择以下场景：\n'
        for i in range(len(self.pdict['scenes'])):
                content = content + str(i)+'.'+self.pdict['scenes'][i]+'  '
        content = content + "\n输入序号选择场景，或输入s+prompt创建自己的场景,举例：\n“s男主角推门进入房间，【name】正在情人旅馆中等着男主角前来约会”"
        self.period = 'cfm_scene'
        self.accinp = 1 
        return content 

    def confirm_scene(self,input):
        # period 'cfm_scene'
        try:
            if input[0] == 's':
                self.init_prompt = input[1:]
                content = "正在前往自定场景……"
                self.now = self.now + 1 
                self.period = 0 
                self.accinp = 0
                return content
            else:
                i = int(input)
                self.init_prompt = self.pdict['init_prompt'][i]
                content = "正在前往{}……".format(self.pdict['scenes'][i])
                self.now = self.now + 1 
                self.period = 0 
                self.accinp = 0
                return content
        except:
            content = '请正确输入'
            self.accinp = 1    
            return content
         
    def cmdline_run(self):
        while(1):
            if self.debug == 1 :
                if self.accinp == 0:
                    r = self.scheduler("0")
                else:
                    x = input()
                    r = self.scheduler(x)  
                if r == '0':
                    pass  
                else:
                    print(r)
            else:
                try:
                    if self.accinp == 0:
                        r = self.scheduler("0")
                    else:
                        
                        x = input()
                        r = self.scheduler(x)  
                    if r == '0':
                        pass  
                    else:
                        print(r)
                except SystemExit:
                    print('the end')
                    sys.exit()
                except Exception as e:
                    print('error:',e)


    def dating(self):
        while(1):
            #self.scheduler()
            if self.debug == 1:
                self.scheduler()
            else:
                try:
                    self.scheduler()
                except SystemExit:
                    print('the end')
                    sys.exit()
                except Exception as e:
                    print('error:',e)
            

if __name__ == "__main__":
    aic = aicrush(apikey,'a')
    aic.cmdline_run()
