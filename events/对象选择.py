def event_对象选择(self):
    charalist=[]
    gradient_text = ""
    ImgList=[]
    for i in self.console.init.chara_ids:
        if self.charater_pwds.get(i).get('小地图') == self.charater_pwds.get('0').get('小地图') :
            charalist.append(i)
    for i in charalist:
        img=''
        charaname= self.console.init.charaters_key.get(i).get('名前')
        gradient_text += self.cs(charaname).click(i) + "   "
        img=img+i+'_'+self.console.init.charaters_key[i].get('draw_type')+'_'+'別顔_服_通常'+'_'+'i'
        #还要有一个事件去获取角色当前的状态，高兴也好伤心也罢生气也罢，然后在那个事件里面返回一个立绘名，在这个搓出来之前我就用普通的表情了
        ImgList.append(img)
        #构思里是这样的应该，然后有一个函数应该给角色key中添加角色当前应该输出的立绘名，立绘类型也是
    return gradient_text,ImgList