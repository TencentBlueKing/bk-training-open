<template>
    <div class="body">
        <bk-divider align="left" style="margin-bottom:30px;">
            <div class="container_title">管理组员</div>
        </bk-divider>
        <div class="container">
            <div class="left_container">
                <div>
                    <bk-badge class="mr15" :theme="'danger'" :max="99" :val="5">
                        <bk-dropdown-menu ref="dropdown" style="width: 261px;display: inline-block;">
                            <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
                                <span>处理新的申请</span>
                                <i :class="['bk-icon icon-angle-down', { 'icon-flip': false }]"></i>
                            </div>
                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                <li>
                                    <div class="content">newperson 申请加入组 group1</div>
                                    <div style="margin-top: 5px">
                                        <bk-container :col="24" :margin="6">
                                            <bk-row>
                                                <bk-col :span="5" :offset="10">
                                                    <bk-button :theme="'primary'" :title="'主要按钮'" size="small">
                                                        同意
                                                    </bk-button>
                                                </bk-col>
                                                <bk-col :span="8" :offset="1">
                                                    <bk-button :theme="'danger'" :title="'主要按钮'" size="small">
                                                        拒绝
                                                    </bk-button>
                                                </bk-col>
                                            </bk-row>
                                        </bk-container>
                                    </div>
                                </li>
                                <li>
                                    <div class="content">newperson2 申请加入组 group1</div>
                                    <div style="margin-top: 5px">
                                        <bk-container :col="24" :margin="6">
                                            <bk-row>
                                                <bk-col :span="5" :offset="10">
                                                    <bk-button :theme="'primary'" :title="'主要按钮'" size="small">
                                                        同意
                                                    </bk-button>
                                                </bk-col>
                                                <bk-col :span="8" :offset="1">
                                                    <bk-button :theme="'danger'" :title="'主要按钮'" size="small">
                                                        拒绝
                                                    </bk-button>
                                                </bk-col>
                                            </bk-row>
                                        </bk-container>
                                    </div>
                                </li>
                            </ul>
                        </bk-dropdown-menu>
                    </bk-badge>
                </div>
                <div style="margin-top: 18px">
                    <bk-select :disabled="false" v-model="selectGroupId" style="width: 261px;display: inline-block;"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                        @change="changeGroup(selectGroupId)"
                        placeholder="选择组"
                        searchable>
                        <bk-option v-for="group in groupList"
                            :key="group.id"
                            :id="group.id"
                            :name="group.name">
                        </bk-option>
                    </bk-select>
                </div>
                <div style="margin-top:18px;height: 600px">
                    <div class="date_picker">
                        <bk-date-picker class="mr15" style="position:relative;" v-model="curDate"
                            :placeholder="'选择日期'"
                            open="true"
                            @change="changeDate(curDate)"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption">
                        </bk-date-picker>
                    </div>
                </div>
            </div>
            <div class="right_container">
                <div v-if="!currentGroupDaily.length" style="margin: 200px auto;width:140px;">
                    没有日报内容哟~
                </div>
                <div v-else>
                    <div style="display: flex;justify-content: flex-end">
                        <bk-badge class="mr15" :theme="'danger'" :max="99" :val="hasNotSubmitMember.length">
                            <bk-dropdown-menu ref="dropdown" style="width: 190px;display: inline-block;">
                                <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
                                    <span>今日未提交报告名单</span>
                                    <i :class="['bk-icon icon-angle-down', { 'icon-flip': false }]"></i>
                                </div>
                                <ul class="bk-dropdown-list" slot="dropdown-content">
                                    <li v-for="member in hasNotSubmitMember" :key="member.id"><a href="javascript:;">{{ member.name }}</a></li>
                                </ul>
                            </bk-dropdown-menu>
                        </bk-badge>
                        <bk-button :theme="'primary'" type="submit" :title="'基础按钮'" class="mr10" @click="remindAll">
                            一键提醒
                        </bk-button>
                    </div>
                    <div class="cards">
                        <div v-for="daliy in hasSubmitDaily" :key="daliy.user.id" class="flexcard">
                            <bk-card class="card" :show-head="true" :show-foot="true">
                                <div slot="header" class="head-main">
                                    {{daliy.user.name}}的日报
                                </div>
                                <div>
                                    <h3 style="height: 25px;overflow: hidden">日报状态：<span v-if="daliy.evaluate.length" style="color: #42b983;font-size: 18px;">已点评</span><span v-else style="color: #ea3636;font-size: 18px;">未点评</span></h3>
                                </div>
                                <div slot="footer" class="foot-main">
                                    <div class="noComment">
                                        <div>
                                            <bk-button :theme="'primary'" :title="'发送提醒'" class="mr10" @click="openDialog(daliy)">
                                                查看他(她)的日报
                                            </bk-button>
                                        </div>
                                    </div>
                                </div>
                            </bk-card>
                        </div>
                        <bk-dialog v-model="daliyDetialDialog.visible" title="日报内容"
                            :header-position="daliyDetialDialog.headerPosition"
                            :width="daliyDetialDialog.width"
                            :position="{ top: 20, left: 100 }">
                            <div>
                                <bk-input :placeholder="dialogMember.content" :type="'textarea'" font-size="large"
                                    :rows="10" style="margin-bottom: 15px; color: #000000" :readonly="true">
                                </bk-input>
                            </div>
                            <div>
                                <h2 v-if="dialogMember.evaluate.length">点评情况</h2>
                                <bk-input v-for="evaluate in dialogMember.evaluate" :key="evaluate" :placeholder="evaluate" :type="'textarea'" font-size="large"
                                    :rows="3" style="margin: 5px 0;" :readonly="true">
                                </bk-input>
                            </div>
                            <div>
                                <h2>点评一下</h2>
                                <bk-input :placeholder="'请输入'" :type="'textarea'" font-size="large" v-model="myComment"
                                    :rows="3" style="margin: 15px 0;">
                                </bk-input>
                            </div>
                            <div slot="footer" class="dialog-foot">
                                <div>
                                    <bk-button :theme="'primary'" :title="'提交'" class="mr10" size="large" @click="submitMyComment(dialogMember)">
                                        {{ !!myComment.length ? '提交' : '确认'}}
                                    </bk-button>
                                </div>
                            </div>
                        </bk-dialog>
                    </div>
                </div>
            </div>
            <!-- 清除浮动，撑开盒子 -->
            <div style="clear:both;"></div>
        </div>
    </div>
</template>

<script>
    export default {
        components: {},
        data () {
            return {
                groupList: [{ id: 1, name: 'group1' }, { id: 0, name: 'group0' }],
                currentGroup: [{ id: 0, name: 'cyb' }, { id: 1, name: 'yjc' }, { id: 2, name: 'zkw' }, { id: 3, name: 'djf' }, { id: 4, name: 'ylh' }],
                currentGroupDaily: [{ content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [], star_level: 0 },
                                    { content: '', evaluate: [], star_level: 0 },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: ['可以', '很好', '很好', '很好', '很好', '很好'], star_level: 4 },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [], star_level: 0 },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [], star_level: 0 }],
                // 日报详细dialog参数
                daliyDetialDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                // 当前打开的日报是哪个组员
                dialogMember: { user: { id: 0, name: 'cyb' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [], star_level: 0 },
                // 我的评分和评论信息
                judgeRate: 5,
                myComment: '',
                // 日历样式
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                // 当天日期
                curDate: new Date(),
                formatDate: '',
                // 选择的组名
                selectGroupName: '',
                selectGroupId: 0,
                hasSubmitDaily: [],
                hasNotSubmitMember: []
            }
        },
        created () {
            this.init()
        },

        methods: {
            init () {
                const date = new Date()
                const paramDate = date.getFullYear() + '-' + (date.getMonth() >= 9 ? (date.getMonth() + 1) : '0' + (date.getMonth() + 1)) + '-' + (date.getDate() > 9 ? (date.getDate()) : '0' + (date.getDate()))
                this.formatDate = paramDate
                // TODO => 发送请求，获取所有用户的信息
                // this.$http.get('/get_groups/').then(res => {
                //     this.groupList = res.data.group_name
                //     this.currentGroup = res.user_name
                //     this.currentGroupDaily = res.user_dairy
                //     this.selectGroupId = res.group_name[0].id
                //     this.selectGroupName = res.group_name[0].name
                // })
                this.judgeSubmit()
            },
            // 判断当前用户有没有交日报
            // hasNotSubmit (member) {
            //     return Object.keys(member.content).length === 0
            // },
            // 提醒用户写日报
            remindAll () {
                // TODO => 发出提醒
                // this.$http.get('/remind_all/',{params:{group_id:selectGroupId,time:this.formatDate}).then(res => {
                //     this.currentGroup = res.user_name
                //     this.currentGroupDaily = res.user_dairy
                //     this.selectGroupName = selectGroupName
                // })
            },
            // 打开日报详情
            openDialog (daily) {
                this.dialogMember = daily
                this.daliyDetialDialog.visible = true
            },
            // 提交我的点评信息
            submitMyComment (dialogMember) {
                if (this.myComment.length) {
                    const alertDialog = this.$bkInfo({
                        type: 'success',
                        title: '点评成功！+ comment = ' + this.myComment,
                        showFooter: false
                    })
                    // TODO => 发送请求，将我的点评和评星提交给后台(评论是否要匿名呢？)
                    // this.$http.get('/send_comment/',{params:{time:this.formatDate,name:dialogMember.user.name,evaluate:this.myComment}).then(res => {
                    //     if(res.message){
                    //         setTimeout(() => {
                    //             alertDialog.close()
                    //         }, 500)
                    //         this.daliyDetialDialog.visible = false
                    //     }else{return false}
                    // })
                    setTimeout(() => {
                        alertDialog.close()
                    }, 500)
                }
                this.daliyDetialDialog.visible = false
            },
            // 改变日历的日期
            changeDate (date) {
                const paramDate = date.getFullYear() + '-' + (date.getMonth() >= 9 ? (date.getMonth() + 1) : '0' + (date.getMonth() + 1)) + '-' + (date.getDate() > 9 ? (date.getDate()) : '0' + (date.getDate()))
                this.formatDate = paramDate
                // this.$http.get('/get_chosen_groups/',{params:{group_name:selectGroupName,time:this.formatDate}).then(res => {
                //     this.currentGroup = res.user_name
                //     this.currentGroupDaily = res.user_dairy
                //     this.selectGroupName = selectGroupName
                //     this.selectGroupId = res.group_name[0].id
                //     this.selectGroupName = res.group_name[0].name
                // })
                this.judgeSubmit()
            },
            // 改变当前查看组名
            changeGroup (selectGroupName) {
                // TODO => 发送请求，获取选定组的信息
                // this.$http.get('/get_chosen_groups/',{params:{group_id:selectGroupId,time:this.formatDate}).then(res => {
                //     this.currentGroup = res.user_name
                //     this.currentGroupDaily = res.user_dairy
                //     this.selectGroupName = selectGroupName
                //     this.selectGroupId = res.group_name[0].id
                //     this.selectGroupName = res.group_name[0].name
                // })
                this.judgeSubmit()
            },
            // 可以复用，等接收到参数，将所有逻辑放这里面
            judgeSubmit () {
                const temyes = []
                const temno = []
                for (let i = 0; i < this.currentGroupDaily.length; i++) {
                    if (this.currentGroupDaily[i].content.length === 0) {
                        temno.push(this.currentGroup[i])
                    } else {
                        const tem = this.currentGroupDaily[i]
                        tem.user = this.currentGroup[i]
                        temyes.push(tem)
                    }
                }
                this.hasSubmitDaily = temyes
                this.hasNotSubmitMember = temno
            }
        }
    }
</script>

<style scoped>
/*@import "./index.css";*/
.body{
    border: 2px solid #EAEBF0 ;
    /* border-radius: 4px; */
    margin:0px 100px;
    padding: 20px 50px;

}
.container_title {
    font-size: 22px;
    font-weight: 700;
}
.left_container{
    float: left;
    width: 360px;
    padding-left: 20px;
    border-right: 1px solid #EAEBF0;
}
.users_list >>> .bk-button{
    margin-bottom: 10px;

}
.right_container{
    float: right;
    min-width: 380px;
    width: calc(100% - 380px);
}
.head-main{
    height: 100%;
    overflow: hidden;
}
.cards{
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    width: 100%;
}
.flexcard{
    width: 24%;
    margin: 10px 0.5%;
}
.card >>> .bk-card-body{
    height: 200px;
    padding: 0 20px;
    background-color: #eeeeee;
    overflow: hidden;
}
.date_picker >>>.bk-date-picker-dropdown{
    top: 32px !important;
}
.foot-main {
    width: 100%;
    height: 100%;
    background: #fafbfd;
    color: #979ba5;
    text-align: center;
    font-size: 28px;
    overflow: hidden;
}
.noSubmitDiv{
    font-size: 20px;
    padding-top: 5px;
}
.hasComment{
    display: flex;
    justify-content: center;
    padding: 10px 0;
}
.hasComment >>> .bk-score-group{
    margin: 0;
}
/*下拉菜单*/
.dropdown-trigger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #c4c6cc;
    height: 32px;
    min-width: 68px;
    border-radius: 2px;
    padding: 0 15px;
    color: #63656E;
}
.dropdown-trigger-btn.bk-icon {
    font-size: 18px;
}
.dropdown-trigger-btn .bk-icon {
    font-size: 22px;
}
.dropdown-trigger-btn:hover {
    cursor: pointer;
    border-color: #979ba5;
}
</style>
