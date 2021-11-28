<template>
    <div class="body">
        <bk-divider align="left" style="margin-bottom:30px;">
            <div class="container_title">管理组</div>
        </bk-divider>
        <div class="container">
            <div class="top_container">
                <div style="margin-left:0.5%">
                    <bk-badge class="mr15" :theme="'danger'" :max="99" :val="newApplyData.length">
                        <bk-button :theme="'primary'" class="mr10" @click="newApplyDialog.visible = true">查看新的申请入组</bk-button>
                    </bk-badge>
                </div>
                <bk-dialog v-model="newApplyDialog.visible" title="新人入组请求"
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
                                <bk-button class="mr10" theme="primary" text @click="dealNewApply(props.row,1)">同意</bk-button>
                                <bk-button class="mr10" theme="primary" text @click="dealNewApply(props.row,2)">拒绝</bk-button>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </bk-dialog>
                <div>
                    <bk-select :disabled="false" v-model="selectGroupId" style="width: 261px;display: inline-block;"
                        @change="changeGroup(selectGroupId)"
                        placeholder="选择组"
                        searchable>
                        <bk-option v-for="item in groupList"
                            :key="item.id"
                            :id="item.id"
                            :name="item.name">
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
                <bk-dialog v-model="hasNotSubmitDialog.visible" title="今日未提交报告名单"
                    :header-position="hasNotSubmitDialog.headerPosition"
                    :width="hasNotSubmitDialog.width"
                    :position="{ top: 20, left: 100 }">
                    <div>
                        <bk-button v-for="daily in hasNotSubmitMember" :key="daily.create_name" :theme="'primary'" style="width:130px;" class="mr10">
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
                                            <bk-button :theme="'primary'" :title="'查看日报'" class="mr10" @click="openDialog(daily)">
                                                查看日报
                                            </bk-button>
                                        </div>
                                    </div>
                                </div>
                            </bk-card>
                        </div>
                        <bk-dialog v-model="dailyDetailDialog.visible" title="日报内容"
                            :header-position="dailyDetailDialog.headerPosition"
                            :width="dailyDetailDialog.width"
                            :position="{ top: 20, left: 100 }">
                            <div v-for="(val, key) in dialogMember.content" :key="key">
                                <h3>{{key}}</h3>
                                <bk-input :placeholder="val" :type="'textarea'" font-size="large"
                                    :rows="2" style="margin-bottom: 15px; color: #000000" :readonly="true">
                                </bk-input>
                            </div>
                            <div v-if="dialogMember.evaluate.length">
                                <h2>点评情况</h2>
                                <div style="max-height: 190px; overflow: scroll">
                                    <bk-input v-for="evaluate in dialogMember.evaluate" :key="evaluate" :placeholder="evaluate.name + '说：' + evaluate.evaluate" :type="'textarea'" font-size="large"
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
                                    <bk-button :theme="'primary'" :title="'确认'" class="mr10" size="large" @click="submitMyComment">
                                        {{ myComment.length ? '提交' : '确认' }}
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
                newApplyData: [],
                // 当前打开的日报详情
                dialogMember: {
                    evaluate: []
                },
                // 我评论信息
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
                // 选择的组
                selectGroupId: 0,
                hasRemindAll: false
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
                this.$http.get('/notice_non_report_users/' + this.selectGroupId + '/?date=' + this.formatDate)
                this.hasRemindAll = true
                this.hasNotSubmitDialog.visible = false
                this.$bkMessage({ theme: 'success', message: '发送成功' })
            },
            // 打开日报详情
            openDialog (daily) {
                this.dialogMember = daily
                this.dailyDetailDialog.visible = true
            },
            // 提交我的点评信息
            submitMyComment () {
                if (this.myComment.length) {
                    // 发送请求，将我的点评提交给后台
                    this.$http.post(
                        '/evaluate_daily/',
                        { daily_id: this.dialogMember.id, evaluate: this.myComment }
                    ).then(res => {
                        if (res.message) {
                            for (const daily of this.memberDaily) {
                                if (daily.id === this.dialogMember.id) {
                                    this.daily.evaluate.push({ 'name': this.$store.state.user.username, evaluate: this.myComment })
                                }
                            }
                            this.dailyDetailDialog.visible = false
                        }
                    })
                    this.$bkMessage({ theme: 'success', message: '点评成功' })
                }
                this.myComment = ''
                this.getDaily(this.selectGroupId, this.formatDate)
                this.dailyDetailDialog.visible = false
            },
            // 封装getDaily请求
            getDaily (id, date) {
                this.$http.get(
                    '/list_member_daily/' + id + '/?date=' + date
                ).then(res => {
                    this.memberDaily = res.data
                })
            },
            // 改变日历的日期
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                this.getDaily(this.selectGroupId, this.formatDate)
            },
            // 改变当前查看组
            changeGroup (selectGroupId) {
                this.selectGroupId = selectGroupId
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
                    if (res.message) {
                        for (const i in this.newApplyData) {
                            if (this.newApplyData[i].hasOwnProperty('user_id') && this.newApplyData[i].user_id === row.user_id) {
                                this.newApplyData.splice(i, 1)
                            }
                        }
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
