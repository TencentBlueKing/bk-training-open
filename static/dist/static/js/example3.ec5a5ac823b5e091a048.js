(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[5],{100:function(e,t,i){"use strict";i.r(t);var s=i(101);var a=i.n(s);for(var n in s)if(n!=="default")(function(e){i.d(t,e,function(){return s[e]})})(n);t["default"]=a.a},101:function(e,t,i){"use strict";var s=i(0);Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;i(30);i(88);var a=s(i(21));var n=s(i(32));var r=s(i(22));var o=s(i(109));var u=s(i(110));var l=s(i(111));var c=s(i(89));var d=s(i(240));var m=s(i(241));var p=i(246);var f=s(i(31));var h=f.default.getallGroups,g=f.default.getGroupInfo,v=f.default.getAllUsers,b=f.default.getUser,G=f.default.addGroup,k=f.default.getNotJoinGroup,_=f.default.deleteGroup,w=f.default.getGroupUsers,A=f.default.addGroupUsers,I=f.default.deleteGroupUsers,y=f.default.updateGroup,D=f.default.ApplyJoinGroup;var U={components:{bkSelect:m.default,bkOption:d.default,bkDialog:c.default,bkTable:l.default,bkTableColumn:u.default,bkButton:o.default},data:function e(){return{isAdmin:"",curGroupId:"",AllgGroupsist:[],curGroupData:[],AllUsers:[],isshowDialog:false,dialogTitle:"",selectAdminIDList:[],selectAdminList:[],newGroup:"",myMsg:{},NotJoinGroup:[],selectJoinGroup:[],selectCompileadminID:[],selectCompileadminList:[],groupUsers:[],notakeUsers:[],tableSelect:[],funcName:"",size:"small",selectnotakeUsersID:[],pagination:{current:1,count:100,limit:10}}},computed:{dialogConfirm:function e(){var t=function e(){};if(this.funcName==="addGroup"){t=this.confirmAdd}else if(this.funcName==="applyJoinGroup"){t=this.confirmApplyJoinGroup}else if(this.funcName==="compileGroup"){t=this.compileGroup}else if(this.funcName==="addGroupUser"){t=this.compileaddGroupUser}return t},dialogCancel:function e(){var t=function e(){};if(this.funcName==="addGroup"){t=this.cancelAdd}else if(this.funcName==="applyJoinGroup"){t=this.cancelApplyJoinGroup}else if(this.funcName==="compileGroup"){t=this.cancelcompileGroup}else if(this.funcName==="addGroupUser"){t=this.canceladdGroupUser}return t},renderGroupUsers:function e(){return this.groupUsers.slice((this.pagination.current-1)*this.pagination.limit,this.pagination.current*this.pagination.limit)}},created:function e(){var t=this;b().then(function(e){t.myMsg=e.data});v().then(function(e){t.AllUsers=e});h().then(function(e){if(e.data.length!==0){t.AllgGroupsist=e.data;t.curGroupId=e.data[0].id;t.curGroupname=e.data[0].name;g(t.curGroupId).then(function(e){t.curGroupData=e.data;t.isAdmin=(0,p.isAdmin)(t.myMsg.username,e.data.admin);t.adminIdList()});w(t.curGroupId).then(function(e){t.groupUsers=e.data;t.pagination.count=e.data.length})}});k().then(function(e){t.NotJoinGroup=e})},methods:{changeGroup:function e(t){var i=this;this.curGroupId=t;g(t).then(function(e){i.curGroupData=e.data;i.isAdmin=(0,p.isAdmin)(i.myMsg.username,e.data.admin)});w(t).then(function(e){i.groupUsers=e.data;i.pagination.count=e.data.length})},executeFunc:function e(t,i){if(t==="compileGroup"){this.adminIdList();this.getadminMsg()}if(t==="addGroupUser"){this.filternoGroupUser()}this.isshowDialog=true;this.funcName=t;this.dialogTitle=i},confirmAdd:function e(){var t=this;if(this.newGroup===""){this.handleBox({theme:"error",message:"请补全内容",offsetY:80});return}this.myMsg.display_name=this.myMsg.name;this.selectAdminList.unshift(this.myMsg);this.AllUsers.forEach(function(e){if(t.selectAdminIDList.includes(e.id)){t.selectAdminList.push(e)}});G({name:this.newGroup,admin:this.selectAdminList}).then(function(e){t.$bkMessage({offsetY:80,message:"添加成功",theme:"success"});t.isshowDialog=false;h().then(function(i){t.AllgGroupsist=i.data;t.changeGroup(e.data.group_id)})});this.newGroup="";this.selectAdminIDList=[];this.selectAdminList=[]},cancelAdd:function e(){this.newGroup="";this.selectAdminIDList=[];this.selectAdminList=[]},handleBox:function e(t){this.$bkMessage(t)},confirmApplyJoinGroup:function e(){var t=this;return(0,r.default)(a.default.mark(function e(){var i;return a.default.wrap(function e(s){while(1){switch(s.prev=s.next){case 0:i=(0,n.default)(t.selectJoinGroup);Promise.all((0,n.default)(i.map(function(e){return D({group_id:e})}))).then(function(e){k().then(function(e){t.selectJoinGroup=[];t.NotJoinGroup=e;t.isshowDialog=false;t.$bkMessage({offsetY:80,message:"申请成功",theme:"success"})})});case 2:case"end":return s.stop()}}},e)}))()},cancelApplyJoinGroup:function e(){this.selectJoinGroup=[]},compileGroup:function e(){var t=this;this.getadminMsg();if(!this.selectCompileadminID.includes(this.myMsg.id)){this.selectCompileadminList.push(this.myMsg)}y(this.curGroupId,{name:this.curGroupData.name,admin:this.selectCompileadminList}).then(function(e){t.$bkMessage({offsetY:80,message:"编辑成功",theme:"success"});t.isshowDialog=false;t.selectCompileadminList=[];t.selectCompileadminID=[];h().then(function(e){t.AllgGroupsist=e.data;t.changeGroup(t.curGroupId)})})},adminIdList:function e(){this.selectCompileadminID=this.curGroupData.admin_list.map(function(e){return e.id})},getadminMsg:function e(){var t=this;this.selectCompileadminList=[];this.AllUsers.forEach(function(e){if(t.selectCompileadminID.includes(e.id)){t.selectCompileadminList.push(e)}})},delete_Group:function e(){var t=this;this.$bkInfo({title:"确认要删除？",confirmFn:function e(){_(t.curGroupId).then(function(e){if(e.result){h().then(function(e){if(e.data.length!==0){t.AllgGroupsist=e.data;t.curGroupId=e.data[0].id;t.curGroupname=e.data[0].name;g(t.curGroupId).then(function(e){t.curGroupData=e.data;w(t.curGroupId).then(function(i){t.groupUsers=i.data;t.pagination.count=i.data.length;t.isAdmin=(0,p.isAdmin)(t.myMsg.username,e.data.admin)})})}else{t.curGroupData=[];t.curGroupId="";t.groupUsers=[]}t.$bkMessage({offsetY:80,message:"删除成功",theme:"success"})})}else{t.$bkMessage({offsetY:80,message:"删除失败",theme:"error"})}})}})},LimitChange:function e(t){this.pagination.limit=t;this.pagination.current=1},handlePageChange:function e(t){this.pagination.current=t},compileaddGroupUser:function e(){var t=this;if(this.selectnotakeUsersID.length!==0){A(this.curGroupId,this.selectnotakeUsersID).then(function(e){if(e.result){t.isshowDialog=false;t.selectnotakeUsersID=[];t.$bkMessage({offsetY:80,message:"新成员添加成功",theme:"success"});t.changeGroup(t.curGroupId)}})}else{this.$bkMessage({offsetY:80,message:"请先选择成员",theme:"error"})}},canceladdGroupUser:function e(){this.isshowDialog=false;this.selectnotakeUsersID=[]},filternoGroupUser:function e(){var t=this.groupUsers.map(function(e){return e.id});this.notakeUsers=this.AllUsers.filter(function(e){if(!t.includes(e.id)){return e}})},removeGroupUser:function e(t){var i=this;var s={user_id:t.id};I(this.curGroupId,s).then(function(e){if(e.result){i.$bkInfo({title:"确认要删除数据？",confirmFn:function e(){i.$bkMessage({offsetY:80,message:"移除成功",theme:"success"});i.changeGroup(i.curGroupId)}})}})},selecchange:function e(t){this.tableSelect=t},alldeleteUsers:function e(){var t=this;if(this.existAdmin()){this.$bkInfo({title:"确认要批量删除数据？",confirmFn:function e(){Promise.all(t.tableSelect.map(function(e){return e.id}).map(function(e){I(t.curGroupId,{user_id:e})})).then(function(e){t.$bkMessage({offsetY:80,message:"成功移除".concat(e.length,"个成员"),theme:"success"});t.changeGroup(t.curGroupId)})}})}},existAdmin:function e(){var t=this;var i=true;if(this.tableSelect.length===0){this.handleBox({theme:"error",message:"未选中成员",offsetY:80});i=false}this.curGroupData.admin_list.map(function(e){return e.id}).forEach(function(e){if(t.tableSelect.map(function(e){return e.id}).includes(e)){t.handleBox({theme:"error",message:"不能选择删除管理员",offsetY:80});i=false}});return i}}};t.default=U},102:function(e,t,i){},246:function(e,t,i){"use strict";Object.defineProperty(t,"__esModule",{value:true});t.isAdmin=void 0;var s=function e(t,i){return i.includes(t)};t.isAdmin=s},247:function(e,t,i){"use strict";var s=i(102);var a=i.n(s);var n=a.a},252:function(e,t,i){"use strict";var s=function(){var e=this;var t=e.$createElement;var i=e._self._c||t;return i("div",{staticClass:"mygroup"},[i("div",{staticClass:"group-msg"},[i("div",{staticClass:"group-msg-groupname"},[i("bk-select",{staticStyle:{width:"250px"},attrs:{behavior:"simplicity",searchable:"","ext-cls":"group-msg-curgroupid",clearable:false},on:{selected:e.changeGroup},model:{value:e.curGroupId,callback:function(t){e.curGroupId=t},expression:"curGroupId"}},e._l(e.AllgGroupsist,function(e){return i("bk-option",{key:e.id,attrs:{id:e.id,name:e.name}})}),1)],1),e._v(" "),i("div",{staticClass:"group-msg-admin"},[i("div",{staticClass:"group-msg-admin-title"},[e._v("管理员: ")]),e._v(" "),i("div",{staticClass:"group-msg-admin-list"},e._l(e.curGroupData.admin_list,function(t,s){return i("div",{key:s,staticClass:"group-msg-admin-item"},[e._v("\n                    "+e._s(t.username)+"("+e._s(t.name)+")\n                    "),s!==e.curGroupData.admin_list.length-1?i("span",{staticStyle:{backgroundColor:"white"}},[e._v(" / ")]):e._e()])}),0)]),e._v(" "),i("div",{staticClass:"group-func"},[i("div",{staticClass:"group-func-major"},[i("bk-button",{staticClass:"group-func-major-item",attrs:{title:"primary",text:true,"hover-theme":"primary"},on:{click:function(t){e.executeFunc("addGroup","新增组")}}},[e._v("\n                    新增小组\n                ")]),e._v(" "),i("bk-button",{staticClass:"group-func-major-item",attrs:{title:"primary",text:true,"hover-theme":"primary"},on:{click:function(t){e.executeFunc("applyJoinGroup","请求入组")}}},[e._v("\n                    请求入组\n                ")]),e._v(" "),i("bk-button",{directives:[{name:"show",rawName:"v-show",value:e.isAdmin,expression:"isAdmin"}],staticClass:"group-func-major-item",attrs:{text:true,"hover-theme":"primary"},on:{click:function(t){e.executeFunc("compileGroup","编辑组")}}},[e._v("\n                    编辑小组\n                ")]),e._v(" "),i("bk-button",{directives:[{name:"show",rawName:"v-show",value:e.isAdmin,expression:"isAdmin"}],staticClass:"group-func-major-item",attrs:{text:true,"hover-theme":"danger"},on:{click:function(t){e.delete_Group()}}},[e._v("\n                    删除小组\n                ")])],1)])]),e._v(" "),i("div",{staticClass:"group-member"},[i("div",{directives:[{name:"show",rawName:"v-show",value:e.isAdmin,expression:"isAdmin"}],staticClass:"group-member-func"},[i("bk-button",{attrs:{"ext-cls":"group-member-func-add"},on:{click:function(t){e.executeFunc("addGroupUser","新增成员")}}},[e._v("\n                新增成员\n            ")]),e._v(" "),i("bk-button",{attrs:{"ext-cls":"group-member-func-batchdel"},on:{click:e.alldeleteUsers}},[e._v("\n                批量删除\n            ")])],1),e._v(" "),i("div",{staticClass:"group-member-renderlist"},[i("bk-table",{attrs:{data:e.renderGroupUsers,size:e.size,pagination:e.pagination},on:{"selection-change":e.selecchange,"page-change":e.handlePageChange,"page-limit-change":e.LimitChange}},[i("bk-table-column",{attrs:{type:"selection",width:"60"}}),e._v(" "),i("bk-table-column",{attrs:{type:"index",label:"序列",width:"60"}}),e._v(" "),i("bk-table-column",{attrs:{label:"用户名",prop:"username"}}),e._v(" "),i("bk-table-column",{attrs:{label:"姓名",prop:"name"}}),e._v(" "),i("bk-table-column",{attrs:{label:"电话",prop:"phone"}}),e._v(" "),i("bk-table-column",{attrs:{label:"邮箱",prop:"email"}}),e._v(" "),i("bk-table-column",{attrs:{label:"操作",width:"150"},scopedSlots:e._u([{key:"default",fn:function(t){return[i("bk-button",{staticClass:"mr10",attrs:{theme:"primary",text:"",disabled:!e.isAdmin||e.curGroupData.admin.includes(t.row.username)},on:{click:function(i){e.removeGroupUser(t.row)}}},[e._v("移除")])]}}])})],1)],1)]),e._v(" "),i("bk-dialog",{staticClass:"group-dialog",attrs:{theme:"primary","mask-close":false,"header-position":e.left,"auto-close":false,title:e.dialogTitle},on:{confirm:function(t){e.dialogConfirm()},cancel:function(t){e.dialogCancel()}},model:{value:e.isshowDialog,callback:function(t){e.isshowDialog=t},expression:"isshowDialog"}},[i("div",{directives:[{name:"show",rawName:"v-show",value:e.funcName==="addGroup",expression:"funcName === 'addGroup'"}]},[i("bk-form",{attrs:{"label-width":"120"}},[i("bk-form-item",{attrs:{label:"组名称",required:"true"}},[i("bk-input",{model:{value:e.newGroup,callback:function(t){e.newGroup=t},expression:"newGroup"}})],1),e._v(" "),i("bk-form-item",{attrs:{label:"管理员"}},[i("bk-select",{attrs:{searchable:"",multiple:"","display-tag":""},model:{value:e.selectAdminIDList,callback:function(t){e.selectAdminIDList=t},expression:"selectAdminIDList"}},e._l(e.AllUsers,function(e){return i("bk-option",{key:e.id,attrs:{id:e.id,name:e.username+"("+e.display_name+")"}})}),1)],1)],1)],1),e._v(" "),i("div",{directives:[{name:"show",rawName:"v-show",value:e.funcName==="applyJoinGroup",expression:"funcName === 'applyJoinGroup'"}]},[i("bk-form",{attrs:{"label-width":"120"}},[i("bk-form-item",{attrs:{label:"组名称",required:"true"}},[i("bk-select",{attrs:{searchable:"",multiple:"","display-tag":""},model:{value:e.selectJoinGroup,callback:function(t){e.selectJoinGroup=t},expression:"selectJoinGroup"}},e._l(e.NotJoinGroup,function(e){return i("bk-option",{key:e.id,attrs:{id:e.id,name:e.group_name}})}),1)],1)],1)],1),e._v(" "),i("div",{directives:[{name:"show",rawName:"v-show",value:e.funcName==="compileGroup",expression:"funcName === 'compileGroup'"}]},[i("bk-form",{attrs:{"label-width":"120"}},[i("bk-form-item",{attrs:{label:"组名称",required:"true"}},[i("bk-input",{model:{value:e.curGroupData.name,callback:function(t){e.$set(e.curGroupData,"name",t)},expression:"curGroupData.name"}})],1),e._v(" "),i("bk-form-item",{attrs:{label:"管理员"}},[i("bk-select",{attrs:{searchable:"",multiple:"","display-tag":""},model:{value:e.selectCompileadminID,callback:function(t){e.selectCompileadminID=t},expression:"selectCompileadminID"}},e._l(e.AllUsers,function(e){return i("bk-option",{key:e.id,attrs:{id:e.id,name:e.username+"("+e.display_name+")"}})}),1)],1)],1)],1),e._v(" "),i("div",{directives:[{name:"show",rawName:"v-show",value:e.funcName==="addGroupUser",expression:"funcName === 'addGroupUser'"}]},[i("bk-form",{attrs:{"label-width":"120"}},[i("bk-form-item",{attrs:{label:"新成员",required:"true"}},[i("bk-select",{attrs:{searchable:"",multiple:"","display-tag":""},model:{value:e.selectnotakeUsersID,callback:function(t){e.selectnotakeUsersID=t},expression:"selectnotakeUsersID"}},e._l(e.notakeUsers,function(e){return i("bk-option",{key:e.id,attrs:{id:e.id,name:e.username+"("+e.display_name+")"}})}),1)],1)],1)],1)])],1)};var a=[];i.d(t,"a",function(){return s});i.d(t,"b",function(){return a})},87:function(e,t,i){"use strict";i.r(t);var s=i(252);var a=i(100);for(var n in a)if(n!=="default")(function(e){i.d(t,e,function(){return a[e]})})(n);var r=i(247);var o=i(4);var u=Object(o["a"])(a["default"],s["a"],s["b"],false,null,"1dbbbc55",null);t["default"]=u.exports}}]);