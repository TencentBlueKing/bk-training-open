(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[6],{233:function(t,e,a){"use strict";var i=a(97);var s=a.n(i);var l=s.a},238:function(t,e,a){"use strict";var i=function(){var t=this;var e=t.$createElement;var a=t._self._c||e;return a("div",{staticClass:"body"},[a("bk-divider",{staticStyle:{"margin-bottom":"30px"},attrs:{align:"left"}},[a("div",{staticClass:"container_title"},[t._v("管理组")])]),t._v(" "),a("div",{staticClass:"container"},[a("div",{staticClass:"top_container"},[a("div",{staticStyle:{width:"24%","max-width":"261px"}},[a("bk-select",{staticStyle:{width:"100%",display:"inline-block"},attrs:{disabled:false,placeholder:"选择组",searchable:""},on:{change:function(e){t.changeGroup(t.selectGroupId)}},model:{value:t.selectGroupId,callback:function(e){t.selectGroupId=e},expression:"selectGroupId"}},t._l(t.groupList,function(t){return a("bk-option",{key:t.id,attrs:{id:t.id,name:t.name}})}),1)],1),t._v(" "),a("div",{staticClass:"date_picker",staticStyle:{width:"24%","max-width":"261px"}},[a("bk-date-picker",{staticStyle:{position:"relative",width:"100%"},attrs:{placeholder:"选择日期",options:t.customOption},on:{change:function(e){t.changeDate(t.curDate)}},model:{value:t.curDate,callback:function(e){t.curDate=e},expression:"curDate"}})],1),t._v(" "),a("div",{staticStyle:{"margin-left":"2%"}},[a("bk-badge",{attrs:{theme:"danger",max:99,val:t.newApplyData.length}},[a("bk-button",{attrs:{theme:"primary"},on:{click:function(e){t.newApplyDialog.visible=true}}},[t._v("\n                        新的申请入组\n                    ")])],1)],1),t._v(" "),a("bk-dialog",{attrs:{title:"新人入组请求","header-position":t.newApplyDialog.headerPosition,width:t.newApplyDialog.width,position:{top:20,left:100}},model:{value:t.newApplyDialog.visible,callback:function(e){t.$set(t.newApplyDialog,"visible",e)},expression:"newApplyDialog.visible"}},[a("bk-table",{staticStyle:{"margin-top":"15px"},attrs:{"virtual-render":true,data:t.newApplyData,height:"200px"}},[a("bk-table-column",{attrs:{prop:"username",label:"用户id"}}),t._v(" "),a("bk-table-column",{attrs:{prop:"name",label:"姓名"}}),t._v(" "),a("bk-table-column",{attrs:{label:"操作",width:"150"},scopedSlots:t._u([{key:"default",fn:function(e){return[a("bk-button",{staticClass:"mr10",attrs:{theme:"primary",text:""},on:{click:function(a){t.dealNewApply(e.row,1)}}},[t._v("\n                                同意\n                            ")]),t._v(" "),a("bk-button",{staticClass:"mr10",attrs:{theme:"primary",text:""},on:{click:function(a){t.dealNewApply(e.row,2)}}},[t._v("\n                                拒绝\n                            ")])]}}])})],1)],1),t._v(" "),a("div",[a("bk-badge",{attrs:{theme:"danger",max:99,val:t.hasNotSubmitMember.length}},[a("bk-button",{attrs:{theme:"primary",title:"未提交"},on:{click:function(e){t.hasNotSubmitDialog.visible=true}}},[t._v("\n                        未提交日报\n                    ")])],1)],1),t._v(" "),a("bk-dialog",{attrs:{title:"今日未提交报告名单","header-position":t.hasNotSubmitDialog.headerPosition,width:t.hasNotSubmitDialog.width,position:{top:20,left:100}},model:{value:t.hasNotSubmitDialog.visible,callback:function(e){t.$set(t.hasNotSubmitDialog,"visible",e)},expression:"hasNotSubmitDialog.visible"}},[a("div",t._l(t.hasNotSubmitMember,function(e){return a("bk-button",{key:e.id,staticClass:"mr10",staticStyle:{width:"130px"},attrs:{theme:"primary"}},[t._v("\n                        "+t._s(e.create_name)+"\n                    ")])}),1),t._v(" "),a("div",{staticClass:"dialog-foot",attrs:{slot:"footer"},slot:"footer"},[a("div",[a("bk-button",{staticClass:"mr10",attrs:{theme:"primary",title:"确认",size:"large",disabled:t.hasRemindAll},on:{click:t.remindAll}},[t._v("\n                            "+t._s(t.hasRemindAll?"已提醒":"一键提醒")+"\n                        ")])],1)])]),t._v(" "),a("div",[a("bk-badge",{attrs:{theme:"danger",max:99,val:t.shareAllList.length}},[a("bk-button",{attrs:{theme:"primary",title:"分享日报"},on:{click:function(e){t.shareAllDialog.visible=true}}},[t._v("\n                        分享日报\n                    ")])],1)],1),t._v(" "),a("bk-dialog",{attrs:{title:"分享日报列表","header-position":t.shareAllDialog.headerPosition,width:t.shareAllDialog.width,position:{top:20,left:100}},model:{value:t.shareAllDialog.visible,callback:function(e){t.$set(t.shareAllDialog,"visible",e)},expression:"shareAllDialog.visible"}},[a("div",[t._l(t.shareAllList,function(e,i){return[a("a",{key:i,staticStyle:{cursor:"pointer"},on:{click:function(e){t.removeFromShareList(i)}}},[a("bk-badge",{key:i,staticClass:"mr15",attrs:{theme:"danger",val:"X"}},[a("bk-button",{key:i,staticStyle:{width:"130px"},attrs:{"hover-theme":"danger"}},[t._v("\n                                    "+t._s(e.create_name)+"\n                                ")])],1)],1)]})],2),t._v(" "),a("div",{staticClass:"dialog-foot",attrs:{slot:"footer"},slot:"footer"},[a("div",[a("bk-button",{staticClass:"mr10",attrs:{theme:"primary",title:"分享",size:"large",disabled:t.hasShareAll||!t.shareAllList.length},on:{click:t.shareAll}},[t._v("\n                            "+t._s(t.hasShareAll?"已分享":"一键分享")+"\n                        ")])],1)])])],1),t._v(" "),a("div",{staticClass:"bottom_container"},[!t.hasSubmitDaily.length?a("div",{staticStyle:{margin:"200px auto",width:"140px"}},[t._v("\n                没有日报内容哟~\n            ")]):a("div",[a("div",{staticClass:"cards"},[t._l(t.hasSubmitDaily,function(e){return a("div",{key:e,staticClass:"flexcard"},[a("bk-card",{staticClass:"card",attrs:{"show-head":true,"show-foot":true}},[a("div",{staticClass:"head-main",attrs:{slot:"header"},slot:"header"},[a("div",{staticClass:"mr20"},[t._v(t._s(e.create_name)+"的日报")]),e.evaluate.length?a("div",{staticStyle:{color:"#3A84FF"}},[t._v("已点评")]):a("div",{staticStyle:{color:"#63656E"}},[t._v("未点评")])]),t._v(" "),a("div",t._l(e.content,function(e,i){return a("div",{key:i},[a("h2",[t._v(t._s(i))]),t._v(" "),a("div",{staticStyle:{"font-size":"18px"}},[a("pre",[t._v(t._s(e))])])])}),0),t._v(" "),e.evaluate.length?a("div",[a("h2",[t._v("点评情况")]),t._v(" "),a("div",t._l(e.evaluate,function(e,i){return a("div",{key:i,staticClass:"singleComment"},[a("span",{staticStyle:{"font-weight":"bold"}},[t._v(t._s(e.name+"说："))]),a("span",[t._v(t._s(e.evaluate))])])}),0)]):t._e(),t._v(" "),a("div",{staticClass:"foot-main",attrs:{slot:"footer"},slot:"footer"},[a("div",[a("bk-button",{staticClass:"mr10",attrs:{theme:"success",title:"分享",size:"small"},on:{click:t.dealShareAll}},[t._v("\n                                        加入待分享\n                                    ")]),t._v(" "),a("bk-button",{staticClass:"mr10",attrs:{theme:"primary",title:"去点评",size:"small"},on:{click:function(a){t.openDialog(e)}}},[t._v("\n                                        去点评\n                                    ")])],1)])])],1)}),t._v(" "),a("bk-dialog",{attrs:{"header-position":t.dailyDetailDialog.headerPosition,width:t.dailyDetailDialog.width,position:{top:20,left:100}},on:{"value-change":t.dailyDetailDialogChange},model:{value:t.dailyDetailDialog.visible,callback:function(e){t.$set(t.dailyDetailDialog,"visible",e)},expression:"dailyDetailDialog.visible"}},[t.dialogMember.hasComment?a("div",[a("h2",[t._v("修改我的点评")]),t._v(" "),a("div",{staticClass:"singleComment"},[a("bk-input",{staticStyle:{margin:"15px 0"},attrs:{type:"textarea","font-size":"large",clearable:true,rows:3},model:{value:t.myNewComment,callback:function(e){t.myNewComment=e},expression:"myNewComment"}})],1)]):a("div",[a("h2",[t._v("我的点评")]),t._v(" "),a("bk-input",{staticStyle:{margin:"15px 0"},attrs:{placeholder:"请输入",clearable:true,type:"textarea","font-size":"large",rows:3},model:{value:t.myComment,callback:function(e){t.myComment=e},expression:"myComment"}})],1),t._v(" "),a("div",{staticClass:"dialog-foot",attrs:{slot:"footer"},slot:"footer"},[a("div",[t.dialogMember.hasComment?[a("bk-button",{staticClass:"mr10",attrs:{theme:"warning",title:"确认修改",size:"large",disabled:t.myNewComment===t.myPastComment},on:{click:function(e){t.operateMyComment(0)}}},[t._v("\n                                        修改\n                                    ")]),t._v(" "),a("bk-button",{staticClass:"mr10",attrs:{theme:"danger",title:"删除评论",size:"large"},on:{click:function(e){t.operateMyComment(1)}}},[t._v("\n                                        删除\n                                    ")])]:t.myComment.length?[a("bk-button",{staticClass:"mr10",attrs:{theme:"primary",title:"确认",size:"large"},on:{click:t.submitMyComment}},[t._v("\n                                        发送给他\n                                    ")])]:t._e(),t._v(" "),a("bk-button",{staticClass:"mr10",attrs:{theme:"default",title:"关闭",size:"large"},on:{click:function(e){t.dailyDetailDialog.visible=false}}},[t._v("\n                                    关闭\n                                ")])],2)])])],2)])])])],1)};var s=[];a.d(e,"a",function(){return i});a.d(e,"b",function(){return s})},82:function(t,e,a){"use strict";a.r(e);var i=a(238);var s=a(95);for(var l in s)if(l!=="default")(function(t){a.d(e,t,function(){return s[t]})})(l);var n=a(233);var r=a(2);var o=Object(r["a"])(s["default"],i["a"],i["b"],false,null,"1a5833b6",null);e["default"]=o.exports},95:function(t,e,a){"use strict";a.r(e);var i=a(96);var s=a.n(i);for(var l in i)if(l!=="default")(function(t){a.d(e,t,function(){return i[t]})})(l);e["default"]=s.a},96:function(t,e,a){"use strict";var i=a(0);Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var s=i(a(85));function l(t,e){var a=typeof Symbol!=="undefined"&&t[Symbol.iterator]||t["@@iterator"];if(!a){if(Array.isArray(t)||(a=n(t))||e&&t&&typeof t.length==="number"){if(a)t=a;var i=0;var s=function t(){};return{s:s,n:function e(){if(i>=t.length)return{done:true};return{done:false,value:t[i++]}},e:function t(e){throw e},f:s}}throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}var l=true,r=false,o;return{s:function e(){a=a.call(t)},n:function t(){var e=a.next();l=e.done;return e},e:function t(e){r=true;o=e},f:function t(){try{if(!l&&a.return!=null)a.return()}finally{if(r)throw o}}}}function n(t,e){if(!t)return;if(typeof t==="string")return r(t,e);var a=Object.prototype.toString.call(t).slice(8,-1);if(a==="Object"&&t.constructor)a=t.constructor.name;if(a==="Map"||a==="Set")return Array.from(t);if(a==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(a))return r(t,e)}function r(t,e){if(e==null||e>t.length)e=t.length;for(var a=0,i=new Array(e);a<e;a++){i[a]=t[a]}return i}var o={data:function t(){return{groupList:[],memberDaily:[],dailyDetailDialog:{visible:false,width:600,headerPosition:"left"},newApplyDialog:{visible:false,width:600,headerPosition:"left"},hasNotSubmitDialog:{visible:false,width:600,headerPosition:"left"},shareAllDialog:{visible:false,width:600,headerPosition:"left"},newApplyData:[],dialogMember:{evaluate:[]},myComment:"",myPastComment:"",myNewComment:"",customOption:{disabledDate:function t(e){if(e>new Date){return true}}},curDate:null,formatDate:"",selectGroupId:0,hasRemindAll:false,shareAllList:[],shareAllIdList:[],hasShareAll:false,currentUserName:this.$store.state.user.username,hasSubmitDaily:[]}},computed:{hasNotSubmitMember:function t(){return this.memberDaily.filter(function(t){return!t.write_status})}},created:function t(){var e=this.$route.query.group;if(e!==undefined){this.selectGroupId=parseInt(e)}var a=this.$route.query.date;if(a!==undefined){this.curDate=new Date(a)}else{this.curDate=new Date}this.formatDate=(0,s.default)(this.curDate).format(s.default.HTML5_FMT.DATE);this.init()},methods:{init:function t(){var e=this;this.$http.get("/list_admin_group/").then(function(t){e.groupList=t.data;if(e.groupList.length>0){if(e.selectGroupId>0){e.changeGroup(e.selectGroupId)}else{e.selectGroupId=e.groupList[0].id}}})},loadApply:function t(){var e=this;this.$http.get("/get_apply_for_group_users/"+this.selectGroupId+"/").then(function(t){e.newApplyData=t.data})},remindAll:function t(){var e=this;this.$http.get("/notice_non_report_users/"+this.selectGroupId+"/?date="+this.formatDate).then(function(t){if(t.result){e.hasRemindAll=true;e.hasNotSubmitDialog.visible=false;e.$bkMessage({theme:"success",message:t.message})}else{e.$bkMessage({theme:"error",message:t.message})}})},shareAll:function t(){var e=this;this.$http.post("/send_evaluate_all/"+this.selectGroupId+"/",{daily_ids:this.shareAllIdList}).then(function(t){if(t.result){e.shareAllDialog.visible=false;e.hasShareAll=true;e.shareAllList=[];e.$bkMessage({theme:"success",message:t.message})}else{e.$bkMessage({theme:"error",message:t.message})}})},dealShareAll:function t(){if(this.shareAllIdList.indexOf(this.dialogMember.id)===-1){this.shareAllList.push(this.dialogMember);this.shareAllIdList.push(this.dialogMember.id);this.$bkMessage({theme:"success",message:"加入成功"})}else{this.$bkMessage({theme:"error",message:"重复加入"})}},removeFromShareList:function t(e){var a=this;this.$bkInfo({title:"确认不再分享"+this.shareAllList[e].create_name+"的日报？",showFooter:true,confirmFn:function t(){a.shareAllList.splice(e,1);a.$bkMessage({theme:"success",message:"移除成功"})}})},openDialog:function t(e){this.dialogMember=e;this.dialogMember.hasComment=false;this.dailyDetailDialog.visible=true;var a=l(this.dialogMember.evaluate),i;try{for(a.s();!(i=a.n()).done;){var s=i.value;if(s.name===this.currentUserName){this.myPastComment=s.evaluate;this.myNewComment=s.evaluate;this.dialogMember.hasComment=true;break}}}catch(t){a.e(t)}finally{a.f()}},hasComment:function t(e){var a=l(e.evaluate),i;try{for(a.s();!(i=a.n()).done;){var s=i.value;if(s.name===this.currentUserName){this.myPastComment=s.evaluate;this.myNewComment=s.evaluate;return true}}}catch(t){a.e(t)}finally{a.f()}return false},submitMyComment:function t(){var e=this;if(this.myComment.length){this.$http.post("/evaluate_daily/",{daily_id:this.dialogMember.id,evaluate:this.myComment}).then(function(t){e.getDaily(e.selectGroupId,e.formatDate).then(function(a){if(t.result){e.dailyDetailDialog.visible=false;e.$bkMessage({theme:"success",message:t.message})}else{e.$bkMessage({theme:"error",message:t.message})}})});this.myComment="";this.dailyDetailDialog.visible=false}},operateMyComment:function t(e){var a=this;if(e===0){this.$http.get("/update_evaluate_daily/"+this.selectGroupId+"/"+this.dialogMember.id+"/?evaluate_content="+this.myNewComment).then(function(t){a.getDaily(a.selectGroupId,a.formatDate).then(function(e){if(t.result){a.dailyDetailDialog.visible=false;a.$bkMessage({theme:"success",message:t.message})}else{a.$bkMessage({theme:"error",message:t.message})}})})}else{this.$http.delete("/delete_evaluate_daily/"+this.selectGroupId+"/"+this.dialogMember.id+"/").then(function(t){a.getDaily(a.selectGroupId,a.formatDate).then(function(e){if(t.result){a.dailyDetailDialog.visible=false;a.$bkMessage({theme:"success",message:t.message})}else{a.$bkMessage({theme:"error",message:t.message})}})})}},getDaily:function t(e,a){var i=this;return this.$http.get("/list_member_daily/"+e+"/?date="+a).then(function(t){i.memberDaily=t.data;i.hasSubmitDaily=i.memberDaily.filter(function(t){return t.write_status});var e=l(i.hasSubmitDaily),a;try{for(e.s();!(a=e.n()).done;){var s=a.value;var n={};for(var r in s.content){if(s.content[r]instanceof Array){var o="";if(s.content.isPrivate){var u=l(s.content[r]),c;try{for(u.s();!(c=u.n()).done;){var m=c.value;o=o+m.content+";\n"}}catch(t){u.e(t)}finally{u.f()}}else{var h=l(s.content[r]),d;try{for(h.s();!(d=h.n()).done;){var f=d.value;o=o+f.content+";-----("+f.cost+")\n"}}catch(t){h.e(t)}finally{h.f()}}n[r]=o}else if(r!=="isPrivate"){n[r]=s.content[r]}}s.content=n}}catch(t){e.e(t)}finally{e.f()}})},changeDate:function t(e){this.formatDate=(0,s.default)(e).format(s.default.HTML5_FMT.DATE);this.shareAllList=[];this.getDaily(this.selectGroupId,this.formatDate)},changeGroup:function t(e){this.selectGroupId=e;this.shareAllList=[];this.getDaily(this.selectGroupId,this.formatDate);this.loadApply()},dealNewApply:function t(e,a){var i=this;this.$http.post("/deal_join_group/"+this.selectGroupId+"/",{user_id:e.user_id,status:a}).then(function(t){if(t.result){for(var a in i.newApplyData){if(i.newApplyData[a].hasOwnProperty("user_id")&&i.newApplyData[a].user_id===e.user_id){i.newApplyData.splice(a,1)}}i.$bkMessage({theme:"success",message:t.message})}else{i.$bkMessage({theme:"error",message:t.message})}})},dailyDetailDialogChange:function t(e){if(e===false){this.myComment=""}}}};e.default=o},97:function(t,e,a){}}]);