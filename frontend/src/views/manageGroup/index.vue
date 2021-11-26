<template>
    <div class="body">
        <bk-divider align="left" style="margin-bottom:30px;">
            <div class="container_title">Admin</div>
        </bk-divider>
        <div class="container">
            <div class="top_container">
                <div style="margin-left:0.5%">
                    <bk-badge class="mr15" :theme="'danger'" :max="99" :val="newApplyData.length">
                        <bk-button :theme="'primary'" class="mr10" @click="newApplyDialog.visible = true">查看新的申请入组</bk-button>
                    </bk-badge>
                </div>
                <div>
                    <bk-select :disabled="false" v-model="selectGroupId" style="width: 261px;display: inline-block;"
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
                <div>
                    <div class="date_picker">
                        <bk-date-picker style="position:relative;" v-model="curDate"
                            placeholder="选择日期"
                            @change="changeDate(curDate)"
                            :options="customOption">
                        </bk-date-picker>
                    </div>
                </div>
                <div>
                    <bk-badge class="mr15" :theme="'danger'" :max="99" :val="hasNotSubmitMember.length">
                        <bk-button :theme="'primary'" type="submit" :title="'基础按钮'" class="mr10" @click="hasNotSubmitDialog.visible = true">
                            今日未提交报告名单
                        </bk-button>
                    </bk-badge>
                </div>
            </div>
            <div class="bottom_container">
                <div v-if="!currentGroupDaily.length" style="margin: 200px auto;width:140px;">
                    没有日报内容哟~
                </div>
                <div v-else>
                    <div class="cards">
                        <div v-for="daliy in hasSubmitDaily" :key="daliy.user.id" class="flexcard">
                            <bk-card class="card" :show-head="true" :show-foot="true">
                                <div slot="header" class="head-main">
                                    {{daliy.user.name}}的日报
                                </div>
                                <div>
                                    <h3 style="height: 25px;overflow: hidden">日报状态：<span v-if="daliy.evaluate.length" style="color: #3A84FF;font-size: 18px;">已点评</span><span v-else style="color: #63656E;font-size: 18px;">未点评</span></h3>
                                </div>
                                <div slot="footer" class="foot-main">
                                    <div class="noComment">
                                        <div>
                                            <bk-button :theme="'primary'" :title="'查看日报'" class="mr10" @click="openDialog(daliy)">
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
                            <div v-if="dialogMember.evaluate.length">
                                <h2>点评情况</h2>
                                <div style="height: 190px; overflow: scroll">
                                    <bk-input v-for="evaluate in dialogMember.evaluate" :key="evaluate" :placeholder="evaluate" :type="'textarea'" font-size="large"
                                        :rows="3" style="margin: 5px 0;" :readonly="true">
                                    </bk-input>
                                </div>
                            </div>
                            <div>
                                <h2>点评一下</h2>
                                <bk-input :placeholder="'请输入'" :type="'textarea'" font-size="large" v-model="myComment"
                                    :rows="3" style="margin: 15px 0;">
                                </bk-input>
                            </div>
                            <div slot="footer" class="dialog-foot">
                                <div>
                                    <bk-button :theme="'primary'" :title="'确认'" class="mr10" size="large" @click="submitMyComment(dialogMember)">
                                        {{ myComment.length ? '提交' : '确认' }}
                                    </bk-button>
                                </div>
                            </div>
                        </bk-dialog>
                        <bk-dialog v-model="newApplyDialog.visible" title="新人入组请求"
                            :header-position="newApplyDialog.headerPosition"
                            :width="newApplyDialog.width"
                            :position="{ top: 20, left: 100 }">
                            <bk-table style="margin-top: 15px;"
                                :virtual-render="true"
                                :data="newApplyData"
                                height="200px">
                                <bk-table-column prop="applier" label="申请人"></bk-table-column>
                                <bk-table-column prop="targetgroup" label="目标组"></bk-table-column>
                                <bk-table-column label="操作" width="150">
                                    <template slot-scope="props">
                                        <bk-button class="mr10" theme="primary" text @click="agreeApply(props.row)">同意</bk-button>
                                        <bk-button class="mr10" theme="primary" text @click="denyApply(props.row)">拒绝</bk-button>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </bk-dialog>
                        <bk-dialog v-model="hasNotSubmitDialog.visible" title="今日未提交报告名单"
                            :header-position="hasNotSubmitDialog.headerPosition"
                            :width="hasNotSubmitDialog.width"
                            :position="{ top: 20, left: 100 }">
                            <div>
                                <bk-button v-for="user in hasNotSubmitMember" :key="user.id" :theme="'primary'" style="width:130px;" class="mr10">
                                    {{user.name}}
                                </bk-button>
                            </div>
                            <div slot="footer" class="dialog-foot">
                                <div>
                                    <bk-button :theme="'primary'" :title="'确认'" class="mr10" size="large" @click="remindAll">
                                        一键提醒
                                    </bk-button>
                                </div>
                            </div>
                        </bk-dialog>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    export default {
        components: {},
        data () {
            return {
                groupList: [{ id: 1, name: 'group1' }, { id: 0, name: 'group0' }],
                currentGroup: [{ id: 0, name: 'cyb' }, { id: 1, name: 'yjc' }, { id: 2, name: 'zkw' }, { id: 3, name: 'djf' }, { id: 4, name: 'ylh' }, { id: 5, name: 'lx' }],
                currentGroupDaily: [{ content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
                                    { content: '', evaluate: [] },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: ['可以', '很好', '很好', '很好', '很好', '很好'] },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
                                    { content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] }],
                // 日报详细dialog参数
                daliyDetialDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                newApplyDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                hasNotSubmitDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                newApplyData: [{ applier: 'cj', targetgroup: 'group0' }, { applier: 'lyz', targetgroup: 'group0' }],
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
                this.formatDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
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
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                // TODO => 发送请求，获取选定日期的信息
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
            },
            agreeApply (row) {
                // TODO => 同意入组
            },
            denyApply (row) {
                // TODO => 拒绝入组
            }
        }
    }
</script>

<style scoped>
.body{
    border: 2px solid #EAEBF0 ;
    margin:0px 100px;
    padding: 20px 50px;

}
.container_title {
    font-size: 22px;
    font-weight: 700;
}
.top_container{
    width: 100%;
    padding: 20px;
    display: flex;
    justify-content: space-between;
}
.bottom_container{
    width: 100%;
    padding: 20px;
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
    height: 150px;
    padding: 0 20px;
    background-color: #eeeeee;
    overflow: hidden;
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
::-webkit-scrollbar{
    display: none;
}
</style>
