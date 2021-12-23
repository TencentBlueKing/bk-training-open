<template>
    <div class="body">
        <div class="container">
            <div class="top_container">
                <div style="width: 24%;max-width:261px">
                    <bk-select
                        :disabled="false"
                        v-model="selectGroupId"
                        style="width: 100%;display: inline-block;"
                        @change="changeGroup(selectGroupId)"
                        placeholder="选择组"
                        searchable>
                        <bk-option
                            v-for="item in groupList"
                            :key="item.id"
                            :id="item.id"
                            :name="item.name">
                        </bk-option>
                    </bk-select>
                </div>
                <div class="date_picker" style="width: 24%;max-width:261px">
                    <bk-date-picker
                        style="position:relative;width: 100%;"
                        v-model="curDate"
                        placeholder="选择日期"
                        @change="changeDate(curDate)"
                        :options="customOption">
                    </bk-date-picker>
                </div>
                <div style="margin-left: 2%">
                    <bk-badge theme="danger" :max="99" :val="newApplyData.length" :visible="newApplyData.length">
                        <bk-button
                            theme="primary"
                            @click="newApplyDialog.visible = true">
                            入组申请
                        </bk-button>
                    </bk-badge>
                </div>
                <bk-dialog
                    v-model="newApplyDialog.visible"
                    title="入组申请"
                    :header-position="newApplyDialog.headerPosition"
                    :width="newApplyDialog.width">
                    <bk-table
                        style="margin-top: 15px;"
                        :virtual-render="true"
                        :data="newApplyData"
                        height="200px">
                        <bk-table-column prop="username" label="用户id"></bk-table-column>
                        <bk-table-column prop="name" label="姓名"></bk-table-column>
                        <bk-table-column label="操作" width="150">
                            <template slot-scope="props">
                                <bk-button
                                    class="mr10"
                                    theme="primary"
                                    text
                                    @click="dealNewApply(props.row,1)">
                                    同意
                                </bk-button>
                                <bk-button
                                    class="mr10"
                                    theme="primary"
                                    text
                                    @click="dealNewApply(props.row,2)">
                                    拒绝
                                </bk-button>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </bk-dialog>
                <div>
                    <bk-badge theme="danger" :max="99" :val="hasNotSubmitMember.length" :visible="hasNotSubmitMember.length">
                        <bk-button
                            theme="primary"
                            title="未提交"
                            @click="hasNotSubmitDialog.visible = true">
                            未提交日报
                        </bk-button>
                    </bk-badge>
                </div>
                <bk-dialog
                    v-model="hasNotSubmitDialog.visible"
                    title="今日未提交报告名单"
                    :header-position="hasNotSubmitDialog.headerPosition"
                    :width="hasNotSubmitDialog.width">
                    <div>
                        <bk-tag v-for="daily in hasNotSubmitMember" :key="daily.id" style="margin: 10px 0" class="mr10">
                            {{daily.create_name}}
                        </bk-tag>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button theme="primary" title="确认" class="mr10" size="large" @click="remindAll" :disabled="hasRemindAll">
                                {{ hasRemindAll ? '已提醒' : '一键提醒' }}
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
                <div>
                    <bk-badge theme="danger" :max="99" :val="shareAllList.length" :visible="shareAllList.length">
                        <bk-button
                            theme="primary"
                            title="分享日报"
                            @click="shareAllDialog.visible = true">
                            分享日报
                        </bk-button>
                    </bk-badge>
                </div>
                <bk-dialog
                    v-model="shareAllDialog.visible"
                    title="分享日报列表"
                    :header-position="shareAllDialog.headerPosition"
                    :width="shareAllDialog.width">
                    <div>
                        <template v-for="(daily,index) in shareAllList">
                            <a :key="index" @click="removeFromShareList(index)" style="cursor:pointer">
                                <bk-badge theme="danger" :val="'X'" :key="index" class="mr15">
                                    <bk-tag
                                        :key="index"
                                        style="margin-bottom: 10px">
                                        {{daily.create_name}}
                                    </bk-tag>
                                </bk-badge>
                            </a>
                        </template>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button
                                theme="primary"
                                title="分享"
                                class="mr10"
                                size="large"
                                @click="shareAll"
                                :disabled="!shareAllList.length">
                                一键分享
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
            </div>
            <div class="bottom_container">
                <div v-if="!hasSubmitDaily.length" style="margin: 200px auto;width:140px;">
                    没有日报内容哟~
                </div>
                <div v-else>
                    <div class="cards">
                        <div v-for="(daily, dindex) in hasSubmitDaily" :key="daily" class="flexcard">
                            <bk-card class="card" :show-head="true" :show-foot="true">
                                <div slot="header" class="head-main">
                                    <div>{{daily.create_name}}的日报</div>
                                    <div class="state-bar">
                                        <bk-tag class="mr15" v-show="!daily.is_normal" theme="warning">补签</bk-tag>
                                        <div v-if="daily.evaluate.length" style="color: #3A84FF;">已点评</div>
                                        <div v-else style="color: #63656E;">未点评</div>
                                    </div>

                                </div>
                                <div>
                                    <div v-for="(dailyContnet, innerIndex) in daily.content" :key="innerIndex">
                                        <h5 style="font-size: 16px !important;margin: 6px 0 !important;">{{dailyContnet.title}}</h5>
                                        <div v-if="dailyContnet.type === 'table'" style="font-size: 18px">
                                            <div v-for="(row, iiIndex) in dailyContnet.content" :key="iiIndex">
                                                <pre class="card-pre">
                                                    <div class="content-wapper">
                                                        <span class="time-wapper">
                                                            <bk-tag v-show="!row.isPrivate && judgeFloatString(row.cost)" theme="info">
                                                                {{typeof row.cost === 'string' ? row.cost : row.cost.toFixed(1) + '小时'}}
                                                            </bk-tag>
                                                            <bk-tag v-show="row.isPrivate || !judgeFloatString(row.cost)" theme="info">
                                                                - -
                                                            </bk-tag>
                                                        </span>
                                                        {{row.text}}
                                                    </div>
                                                </pre>
                                            </div>
                                        </div>
                                        <div style="font-size:14px;line-height: 22px;" v-else>
                                            {{dailyContnet.text}}
                                        </div>
                                    </div>
                                </div>
                                <div v-if="daily.evaluate.length">
                                    <h4>点评情况</h4>
                                    <div>
                                        <div class="singleComment" v-for="(evaluate,index) in daily.evaluate" :key="index">
                                            <p style="font-weight: bold">{{evaluate.name + '：'}}</p>
                                            <span>{{evaluate.evaluate}}</span>
                                        </div>
                                    </div>
                                </div>
                                <div slot="footer" class="foot-main">
                                    <div>
                                        <bk-button
                                            theme="primary"
                                            title="去点评"
                                            class="mr10"
                                            size="small"
                                            @click="openDialog(daily)">
                                            去点评
                                        </bk-button>
                                        <bk-button
                                            theme="primary"
                                            title="去点评"
                                            class="mr10"
                                            size="small"
                                            @click="setPerfect(daily, dindex)">
                                            {{daily.is_perfect ? '取消优秀' : '设为优秀'}}
                                        </bk-button>
                                    </div>
                                </div>
                            </bk-card>
                        </div>
                        <bk-dialog
                            v-model="dailyDetailDialog.visible"
                            :header-position="dailyDetailDialog.headerPosition"
                            :width="dailyDetailDialog.width"
                            title="我的点评"
                            @value-change="dailyDetailDialogChange">
                            <div v-if="dialogMember.hasComment">
                                <div class="singleComment">
                                    <bk-input
                                        v-model="myNewComment"
                                        type="textarea"
                                        font-size="large"
                                        :clearable="true"
                                        :rows="3"
                                        style="margin: 15px 0;">
                                    </bk-input>
                                </div>
                            </div>
                            <div v-else>
                                <bk-input
                                    placeholder="请输入"
                                    :clearable="true"
                                    type="textarea"
                                    font-size="large"
                                    v-model="myComment"
                                    :rows="3"
                                    style="margin: 15px 0;">
                                </bk-input>
                            </div>
                            <div slot="footer" class="dialog-foot">
                                <div>
                                    <bk-button
                                        theme="primary"
                                        title="分享"
                                        class="mr10"
                                        size="large"
                                        @click="dealShareAll(dialogMember)">
                                        加入待分享
                                    </bk-button>
                                    <template v-if="dialogMember.hasComment">
                                        <bk-button
                                            theme="warning"
                                            title="确认修改"
                                            class="mr10"
                                            size="large"
                                            @click="operateMyComment(0)"
                                            :disabled="myNewComment === myPastComment">
                                            修改
                                        </bk-button>
                                        <bk-button
                                            theme="danger"
                                            title="删除评论"
                                            class="mr10"
                                            size="large"
                                            @click="operateMyComment(1)">
                                            删除
                                        </bk-button>
                                    </template>
                                    <template v-else>
                                        <bk-button
                                            theme="primary"
                                            title="确认"
                                            class="mr10"
                                            size="large"
                                            @click="submitMyComment">
                                            保存并发送
                                        </bk-button>
                                    </template>
                                    <bk-button
                                        theme="default"
                                        title="关闭"
                                        class="mr10"
                                        size="large"
                                        @click="dailyDetailDialog.visible = false">
                                        关闭
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
        data () {
            return {
                groupList: [],
                memberDaily: [],
                // 日报详细dialog参数
                dailyDetailDialog: {
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
                shareAllDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                newApplyData: [],
                // 当前打开的日报详情
                dialogMember: {
                    evaluate: [],
                    hasComment: false
                },
                // 我正在评论的信息
                myComment: '',
                // 我之前评论的信息
                myPastComment: '',
                // 我修改的评论信息
                myNewComment: '',
                // 日历样式
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                // 当天日期
                curDate: null,
                formatDate: '',
                // 选择的组
                selectGroupId: 0,
                hasRemindAll: false,
                shareAllList: [],
                shareAllIdList: [],
                hasSharedIdList: [],
                currentUserName: this.$store.state.user.username,
                hasSubmitDaily: [],
                currentGroupAdmin: []
            }
        },
        computed: {
            hasNotSubmitMember () {
                return this.memberDaily.filter((item) => {
                    return !item.write_status && this.currentGroupAdmin.indexOf(item.create_by) === -1
                })
            }
        },
        created () {
            const groupIdInURL = this.$route.query.group
            if (groupIdInURL !== undefined) {
                this.selectGroupId = parseInt(groupIdInURL)
            }
            const dateInURL = this.$route.query.date
            if (dateInURL !== undefined) {
                this.curDate = new Date(dateInURL)
            } else {
                this.curDate = new Date()
            }

            this.formatDate = moment(this.curDate).format(moment.HTML5_FMT.DATE)
        },
        activated () {
            if (!this.groupList.length) {
                this.init()
            } else {
                this.changeGroup(this.selectGroupId)
            }
        },
        methods: {
            init () {
                // 发送请求，获取所有用户的信息
                this.$http.get(
                    '/list_admin_group/'
                ).then(res => {
                    this.groupList = res.data
                    if (this.groupList.length > 0) {
                        if (this.selectGroupId > 0) {
                            this.changeGroup(this.selectGroupId)
                        } else {
                            this.selectGroupId = this.groupList[0].id
                        }
                        this.$http.get(
                            '/list_group_admin/' + this.selectGroupId + '/'
                        ).then(res => {
                            if (res.result) {
                                this.currentGroupAdmin = res.data
                            } else {
                                this.$bkMessage({
                                    theme: 'warning',
                                    message: res.message
                                })
                            }
                        })
                    }
                })
            },
            loadApply () {
                //  获取申请该组的列表
                this.$http.get(
                    '/get_apply_for_group_users/' + this.selectGroupId + '/'
                ).then(res => {
                    this.newApplyData = res.data
                })
            },
            judgeFloatString (value) {
                if (value === '0.0' || value === '0' || !value) {
                    return false
                } else if (typeof value === 'string' && value[0] === '0') {
                    return false
                } else {
                    return true
                }
            },
            // 提醒用户写日报
            remindAll () {
                // 发出一键提醒
                this.$http.post(
                    '/notice_non_report_users/' + this.selectGroupId + '/',
                    { date: this.formatDate }
                ).then(res => {
                    if (res.result) {
                        this.hasRemindAll = true
                        this.hasNotSubmitDialog.visible = false
                        this.$bkMessage({
                            theme: 'success',
                            message: res.message
                        })
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message
                        })
                    }
                })
            },
            // 一键分享给所有组员
            shareAll () {
                this.$http.post(
                    '/send_evaluate_all/' + this.selectGroupId + '/',
                    { daily_ids: this.shareAllIdList }
                ).then(res => {
                    if (res.result) {
                        this.shareAllDialog.visible = false
                        for (const id of this.shareAllIdList) {
                            this.hasSharedIdList.push(id)
                        }
                        this.shareAllIdList = []
                        this.shareAllList = []
                        this.$bkMessage({
                            theme: 'success',
                            message: res.message
                        })
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message
                        })
                    }
                })
            },
            // 添加到待分享列表
            dealShareAll (daily) {
                if (this.hasSharedIdList.indexOf(daily.id) !== -1) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '您已经分享过该日报啦'
                    })
                } else if (this.shareAllIdList.indexOf(daily.id) === -1) {
                    this.shareAllList.push(daily)
                    this.shareAllIdList.push(daily.id)
                    this.$bkMessage({
                        theme: 'success',
                        message: '加入成功'
                    })
                } else {
                    this.$bkMessage({
                        theme: 'error',
                        message: '您已经将该日报加入啦'
                    })
                }
            },
            // 从待分享列表中移除
            removeFromShareList (index) {
                this.$bkInfo({
                    title: '确认不再分享' + this.shareAllList[index].create_name + '的日报？',
                    showFooter: true,
                    confirmFn: () => {
                        this.shareAllList.splice(index, 1)
                        this.shareAllIdList.splice(index, 1)
                        this.$bkMessage({
                            theme: 'success',
                            message: '移除成功'
                        })
                    }
                })
            },
            // 打开日报详情
            openDialog (daily) {
                this.dialogMember = daily
                this.dialogMember.hasComment = false
                this.dailyDetailDialog.visible = true
                for (const singleEvaluate of this.dialogMember.evaluate) {
                    if (singleEvaluate.name === this.currentUserName) {
                        this.myPastComment = singleEvaluate.evaluate
                        this.myNewComment = singleEvaluate.evaluate
                        this.dialogMember.hasComment = true
                        break
                    }
                }
            },
            // 提交我的点评信息
            submitMyComment () {
                if (this.myComment.length) {
                    // 发送请求，将我的点评提交给后台
                    this.$http.post(
                        '/evaluate_daily/',
                        { daily_id: this.dialogMember.id, evaluate: this.myComment }
                    ).then(res => {
                        this.getDaily(
                            this.selectGroupId,
                            this.formatDate
                        ).then(result => {
                            if (res.result) {
                                this.$bkMessage({
                                    theme: 'success',
                                    message: res.message
                                })
                                this.dailyDetailDialog.visible = false
                            } else {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: res.message
                                })
                            }
                        })
                    })
                    this.myComment = ''
                    this.dailyDetailDialog.visible = false
                } else {
                    this.$bkMessage({
                        theme: 'warning',
                        message: '点评内容为空'
                    })
                }
            },
            // 更新，删除评论
            operateMyComment (status) {
                if (status === 0) {
                    this.$http.post(
                        '/update_evaluate_daily/' + this.selectGroupId + '/' + this.dialogMember.id + '/',
                        { evaluate_content: this.myNewComment }
                    ).then(res => {
                        this.getDaily(
                            this.selectGroupId,
                            this.formatDate
                        ).then(result => {
                            if (res.result) {
                                this.dailyDetailDialog.visible = false
                                this.$bkMessage({
                                    theme: 'success',
                                    message: res.message
                                })
                            } else {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: res.message
                                })
                            }
                        })
                    })
                } else {
                    this.$http.delete(
                        '/delete_evaluate_daily/' + this.selectGroupId + '/' + this.dialogMember.id + '/'
                    ).then(res => {
                        this.getDaily(
                            this.selectGroupId,
                            this.formatDate
                        ).then(result => {
                            if (res.result) {
                                this.dailyDetailDialog.visible = false
                                this.$bkMessage({
                                    theme: 'success',
                                    message: res.message
                                })
                            } else {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: res.message
                                })
                            }
                        })
                    })
                }
            },
            // 封装getDaily请求
            getDaily (id, date) {
                return this.$http.get(
                    '/list_member_daily/' + id + '/?date=' + date
                ).then(res => {
                    this.memberDaily = res.data
                    this.hasSubmitDaily = this.memberDaily.filter((daily) => {
                        return daily.write_status
                    })
                })
            },
            // 改变日历的日期
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                this.shareAllList = []
                this.shareAllIdList = []
                this.getDaily(this.selectGroupId, this.formatDate)
            },
            // 改变当前查看组
            changeGroup (selectGroupId) {
                this.selectGroupId = selectGroupId
                this.shareAllList = []
                this.shareAllIdList = []
                // 发送请求，获取选定组的信息
                this.getDaily(this.selectGroupId, this.formatDate)
                // 获取申请该组的列表
                this.loadApply()
            },
            // 处理新的入组申请
            dealNewApply (row, status) {
                this.$http.post(
                    '/deal_join_group/' + this.selectGroupId + '/',
                    { user_id: row.user_id, status: status }
                ).then(res => {
                    if (res.result) {
                        for (const i in this.newApplyData) {
                            if (this.newApplyData[i].hasOwnProperty('user_id') && this.newApplyData[i].user_id === row.user_id) {
                                this.newApplyData.splice(i, 1)
                            }
                        }
                        this.$bkMessage({
                            theme: 'success',
                            message: res.message
                        })
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message
                        })
                    }
                })
            },
            dailyDetailDialogChange (val) {
                if (val === false) {
                    this.myComment = ''
                }
            },
            // 设置/取消优秀日报
            setPerfect (daily, index) {
                this.$http.patch(
                    '/update_daily_perfect_status/' + this.selectGroupId + '/' + daily.id + '/'
                ).then(res => {
                    if (res.result) {
                        this.hasSubmitDaily[index].is_perfect = !daily.is_perfect
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message
                        })
                    }
                })
            }
        }
    }
</script>

<style scoped>
.body{
    border: 2px solid #EAEBF0 ;
    margin:0px 100px;
    padding: 20px 50px;
    min-height: calc(100vh - 140px);
}
.container_title {
    font-size: 22px;
    font-weight: 700;
}
.top_container{
    width: 100%;
    padding: 20px 0.5%;
    display: flex;
    justify-content: space-between;
}
.bk-dialog /deep/ .bk-table .bk-table-header-wrapper .bk-table-header{
  width: 100% !important;
}
.bk-dialog /deep/ .bk-table .bk-table-body-wrapper .bk-table-body{
  width: 100% !important;
}
.bk-dialog /deep/ .bk-table .bk-table-body-wrapper .bk-table-empty-block{
  width: 100% !important;
}
.bottom_container{
    width: 100%;
    padding: 20px 0;
}
.head-main{
    height: 100%;
    display: flex;
    justify-content: space-between;
    overflow: hidden;

}
.head-main .state-bar{
    display: flex;
    align-items: center;
}
.head-main .state-bar .mr15{
    font-size: 14px !important;
}
.cards{
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    width: 100%;
}
.flexcard{
    width: 300px;
    margin: 10px 0.5%;
}
.card{
    cursor: default;
}
.card /deep/ .bk-card-body{
    height: 200px;
    padding: 0 20px;
    overflow-y: scroll;
}
.card /deep/ .bk-card-body .card-pre{
        white-space: normal;
        display: flex;
        flex-wrap: nowrap;
}
.card /deep/ .bk-card-body .card-pre .time-wapper{
        width: 68px;
        margin-right: 6px;
}
.card /deep/ .bk-card-body .card-pre .time-wapper .bk-tag{
    margin: 0 !important;
    padding: 0 !important;
    width: 68px;
    text-align: center;
}
.card /deep/ .bk-card-body .card-pre .content-wapper{
    font-size: 14px;
    line-height: 22px;
}
.card /deep/ .bk-card-body .sub-title{
    font-size: 16px !important;
    margin: 6px 0 !important;
}
pre{
    white-space: pre-wrap;
    word-break: break-word;
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
