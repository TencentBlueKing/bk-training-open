<template>
    <div class="body">
        <bk-divider align="left" style="margin-bottom:30px;">
            <div class="container_title">管理组</div>
        </bk-divider>
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
                    <bk-badge :theme="'danger'" :max="99" :val="newApplyData.length">
                        <bk-button
                            :theme="'primary'"
                            @click="newApplyDialog.visible = true">
                            新的申请入组
                        </bk-button>
                    </bk-badge>
                </div>
                <bk-dialog
                    v-model="newApplyDialog.visible"
                    title="新人入组请求"
                    :header-position="newApplyDialog.headerPosition"
                    :width="newApplyDialog.width"
                    :position="{ top: 20, left: 100 }">
                    <bk-table style="margin-top: 15px;"
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
                    <bk-badge :theme="'danger'" :max="99" :val="hasNotSubmitMember.length">
                        <bk-button
                            :theme="'primary'"
                            :title="'未提交'"
                            @click="hasNotSubmitDialog.visible = true">
                            未提交日报
                        </bk-button>
                    </bk-badge>
                </div>
                <bk-dialog
                    v-model="hasNotSubmitDialog.visible"
                    title="今日未提交报告名单"
                    :header-position="hasNotSubmitDialog.headerPosition"
                    :width="hasNotSubmitDialog.width"
                    :position="{ top: 20, left: 100 }">
                    <div>
                        <bk-button v-for="daily in hasNotSubmitMember" :key="daily.id" :theme="'primary'" style="width:130px;" class="mr10">
                            {{daily.create_name}}
                        </bk-button>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button :theme="'primary'" :title="'确认'" class="mr10" size="large" @click="remindAll" :disabled="hasRemindAll">
                                {{ hasRemindAll ? '已提醒' : '一键提醒' }}
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
                <div>
                    <bk-badge :theme="'danger'" :max="99" :val="shareAllList.length">
                        <bk-button
                            :theme="'primary'"
                            :title="'分享日报'"
                            @click="shareAllDialog.visible = true">
                            分享日报
                        </bk-button>
                    </bk-badge>
                </div>
                <bk-dialog
                    v-model="shareAllDialog.visible"
                    title="分享日报列表"
                    :header-position="shareAllDialog.headerPosition"
                    :width="shareAllDialog.width"
                    :position="{ top: 20, left: 100 }">
                    <div>
                        <template v-for="(daily,index) in shareAllList">
                            <a :key="index" @click="removeFromShareList(index)" style="cursor:pointer">
                                <bk-badge :theme="'danger'" :val="'X'" :key="index" class="mr15">
                                    <bk-button
                                        :key="index"
                                        style="width:130px;"
                                        hover-theme="danger">
                                        {{daily.create_name}}
                                    </bk-button>
                                </bk-badge>
                            </a>
                        </template>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button :theme="'primary'" :title="'分享'" class="mr10" size="large" @click="shareAll" :disabled="hasShareAll || !shareAllList.length">
                                {{ hasShareAll ? '已分享' : '一键分享' }}
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
                        <div v-for="daily in hasSubmitDaily" :key="daily" class="flexcard">
                            <bk-card class="card" :show-head="true" :show-foot="true">
                                <div slot="header" class="head-main">
                                    {{daily.create_name}}的日报
                                </div>
                                <div>
                                    <h3 style="height: 25px;overflow: hidden">点评情况：<span v-if="daily.evaluate.length" style="color: #3A84FF;font-size: 18px;">已点评</span><span v-else style="color: #63656E;font-size: 18px;">未点评</span></h3>
                                </div>
                                <div slot="footer" class="foot-main">
                                    <div class="noComment">
                                        <div>
                                            <bk-button
                                                :theme="'primary'"
                                                :title="'查看日报'"
                                                class="mr10"
                                                @click="openDialog(daily)">
                                                查看日报
                                            </bk-button>
                                        </div>
                                    </div>
                                </div>
                            </bk-card>
                        </div>
                        <bk-dialog
                            v-model="dailyDetailDialog.visible"
                            title="日报内容"
                            :header-position="dailyDetailDialog.headerPosition"
                            :width="dailyDetailDialog.width"
                            :position="{ top: 20, left: 100 }">
                            <div v-for="(val, key) in dialogMember.content" :key="key">
                                <h3>{{key}}</h3>
                                <bk-input
                                    :placeholder="val"
                                    :type="'textarea'"
                                    font-size="large"
                                    :rows="2"
                                    style="margin-bottom: 15px; color: #000000"
                                    :readonly="true">
                                </bk-input>
                            </div>
                            <div v-if="dialogMember.evaluate.length">
                                <h2>点评情况</h2>
                                <div style="max-height: 190px; overflow: scroll">
                                    <div class="singleComment" v-for="(evaluate,index) in dialogMember.evaluate" :key="index">
                                        <bk-input
                                            :type="'textarea'"
                                            font-size="large"
                                            :rows="3" style="margin: 5px 0;"
                                            :placeholder="evaluate.name + '说：' + evaluate.evaluate"
                                            :readonly="true">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                            <div v-if="dialogMember.hasComment">
                                <h2>修改我的点评</h2>
                                <div class="singleComment">
                                    <bk-input
                                        v-model="myNewComment"
                                        :type="'textarea'"
                                        font-size="large"
                                        :clearable="true"
                                        :rows="3"
                                        style="margin: 15px 0;">
                                    </bk-input>
                                </div>
                            </div>
                            <div v-else>
                                <h2>我的点评</h2>
                                <bk-input
                                    :placeholder="'请输入'"
                                    :clearable="true"
                                    :type="'textarea'"
                                    font-size="large"
                                    v-model="myComment"
                                    :rows="3"
                                    style="margin: 15px 0;">
                                </bk-input>
                            </div>
                            <div slot="footer" class="dialog-foot">
                                <div>
                                    <bk-button
                                        :theme="'success'"
                                        :title="'分享'"
                                        class="mr10"
                                        size="large"
                                        @click="dealShareAll">
                                        加入待分享
                                    </bk-button>
                                    <template v-if="dialogMember.hasComment">
                                        <bk-button
                                            :theme="'warning'"
                                            :title="'确认修改'"
                                            class="mr10"
                                            size="large"
                                            @click="operateMyComment(0)"
                                            :disabled="myNewComment === myPastComment">
                                            修改
                                        </bk-button>
                                        <bk-button
                                            :theme="'danger'"
                                            :title="'删除评论'"
                                            class="mr10"
                                            size="large"
                                            @click="operateMyComment(1)">
                                            删除
                                        </bk-button>
                                    </template>
                                    <template v-else-if="myComment.length">
                                        <bk-button
                                            :theme="'primary'"
                                            :title="'确认'"
                                            class="mr10"
                                            size="large"
                                            @click="submitMyComment">
                                            发送给他
                                        </bk-button>
                                    </template>
                                    <bk-button
                                        :theme="'default'"
                                        :title="'关闭'"
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
        components: {},
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
                    evaluate: []
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
                curDate: new Date(),
                formatDate: '',
                // 选择的组
                selectGroupId: 0,
                hasRemindAll: false,
                shareAllList: [],
                shareAllIdList: [],
                hasShareAll: false,
                currentUserName: this.$store.state.user.username
            }
        },
        computed: {
            hasSubmitDaily () {
                return this.memberDaily.filter((item) => {
                    return item.write_status
                })
            },
            hasNotSubmitMember () {
                return this.memberDaily.filter((item) => {
                    return !item.write_status
                })
            }
        },
        watch: {
            'dailyDetailDialog.visible': {
                handler (newvalue, oldvalue) {
                    if (newvalue === false) {
                        this.myComment = ''
                    }
                },
                deep: true
            }
        },
        created () {
            this.formatDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
            this.init()
        },
        methods: {
            init () {
                // 发送请求，获取所有用户的信息
                this.$http.get(
                    '/list_admin_group/'
                ).then(res => {
                    this.groupList = res.data
                    if (this.groupList.length > 0) {
                        this.selectGroupId = this.groupList[0].id
                        this.loadApply()
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
            // 提醒用户写日报
            remindAll () {
                // 发出一键提醒
                this.$http.get(
                    '/notice_non_report_users/' + this.selectGroupId + '/?date=' + this.formatDate
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
                        this.hasShareAll = true
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
            dealShareAll () {
                if (this.shareAllIdList.indexOf(this.dialogMember.id) === -1) {
                    this.shareAllList.push(this.dialogMember)
                    this.shareAllIdList.push(this.dialogMember.id)
                    this.$bkMessage({
                        theme: 'success',
                        message: '加入成功'
                    })
                } else {
                    this.$bkMessage({
                        theme: 'error',
                        message: '重复加入'
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
                    this.myComment = ''
                    this.dailyDetailDialog.visible = false
                }
            },
            // 更新，删除评论
            operateMyComment (status) {
                if (status === 0) {
                    this.$http.get(
                        '/update_evaluate_daily/' + this.selectGroupId + '/' + this.dialogMember.id + '/?evaluate_content=' + this.myNewComment
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
                })
            },
            // 改变日历的日期
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                this.shareAllList = []
                this.getDaily(this.selectGroupId, this.formatDate)
            },
            // 改变当前查看组
            changeGroup (selectGroupId) {
                this.selectGroupId = selectGroupId
                this.shareAllList = []
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
    padding: 20px 0.5%;
    display: flex;
    justify-content: space-between;
}
.bottom_container{
    width: 100%;
    padding: 20px 0;
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
