import openai

def get_g3t_response(messages,api_key = "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",hh=0):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo',
            messages = messages,
            temperature=1
        )
        resText = response.choices[0].message.content
        #print('test:',resText)
        if hh==0:
            return resText.replace('\n','')
        else:
            return resText
    except Exception as e:
        print("error,retry",e)
        return get_g3t_response(messages,api_key,hh)
def hybirdsplit(a):
    a = a.replace(':','：')
    a = a.replace('【真实版回复】','真实版回复：')
    if a.count('：')==2:
        return a.split('：')[2]
    elif a.count('：')==0:
        print('not good!')
        return a 
    else:
        b = a.split('真实')[1].split('：',1)[1]
        return b
        

def keyword_fix(a):
    #关键词返回处理
    try:
        a = a.replace('.','。')
        a = a.replace('。','')
        if a.count('：') == 1:
            return a.split('：')[1]
        return a 
    except:
        print("keyword error:",a)