def event_getpwd(this, id='0'):
    # 检查charater_pwds中是否有该角色
    if id in this.charater_pwds:
        mypwd = this.charater_pwds[id]
        
        this.console.PRINT(f"{this.console.init.charaters_key[id].get('名前')}当前位置....")
        this.console.PRINT(f"[{this.console.init.global_key['map'][mypwd['大地图']]}]" + f"[{this.console.init.global_key['map'][mypwd['小地图']]}]")
    else:
        this.console.PRINT(f"角色ID {id} 不存在", colors=(255, 200, 200))
event_getpwd.event_id = "getpwd"
event_getpwd.event_name = "查看当前位置"
event_getpwd.event_trigger = "2"