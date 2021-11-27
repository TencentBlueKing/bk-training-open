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
                <div v-if="!hasSubmitDaily.length" style="margin: 200px auto;width:140px;">
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
                                    <h3 style="height: 25px;overflow: hidden">点评情况：<span v-if="daliy.evaluate.length" style="color: #3A84FF;font-size: 18px;">已点评</span><span v-else style="color: #63656E;font-size: 18px;">未点评</span></h3>
                                </div>
                                <div slot="footer" class="foot-main">
                                    <div class="noComment">
                                        <div>
                                            <bk-button :theme="'primary'" :title="'查看日报'" class="mr10" @click="openDialog(daliy)">
                                                查看日报
                                            </bk-button>
                                        </div>
                                    </div>
                                </div>
                            </bk-card>
                        </div>
                        <bk-dialog v-model="daliyDetailDialog.visible" title="日报内容"
                            :header-position="daliyDetailDialog.headerPosition"
                            :width="daliyDetailDialog.width"
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
                                    <bk-button :theme="'primary'" :title="'确认'" class="mr10" size="large" @click="remindAll" :disabled="hasRemindAll">
                                        {{ hasRemindAll ? '已提醒' : '一键提醒' }}
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
                // currentGroup: [{ id: 0, name: 'cyb' }, { id: 1, name: 'yjc' }, { id: 2, name: 'zkw' }, { id: 3, name: 'djf' }, { id: 4, name: 'ylh' }, { id: 5, name: 'lx' }],
                hasSubmitDaily: [{ id: 0, user: { id: 0, name: 'cyb' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
                                 { id: 1, user: { id: 1, name: 'ylh' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: ['可以', '很好', '很好', '很好', '很好', '很好'] },
                                 { id: 2, user: { id: 2, name: 'djf' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
                                 { id: 3, user: { id: 3, name: 'lx' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
                                 { id: 4, user: { id: 4, name: 'zkw' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] }],
                // 日报详细dialog参数
                daliyDetailDialog: {
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
                dialogMember: { id: 0, user: { id: 0, name: 'cyb' }, content: '今日任务: 今天干了一些啥事, 明日任务: xxxx, 感想: 继续加油', evaluate: [] },
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
                hasNotSubmitMember: [{ id: 0, name: 'yjc' }],
                hasRemindAll: false
            }
        },
        created () {
            this.formatDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
            this.init()
        },

        methods: {
            init () {
                this.formatDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
                // 发送请求，获取所有用户的信息
                this.$http.get('/list_admin_group/').then(res => {
                    this.groupList = res.data
                    this.selectGroupId = res.data[0].id
                    this.getdata({ params: { group_id: res.data[0].id, date: this.formatDate } })
                })
            },
            // 提醒用户写日报
            remindAll () {
                // 发出一键提醒
                this.$http.post('/notice_non_report_users/', { group_id: this.selectGroupId, date: this.formatDate }).then(res => {
                    if (res.message) {
                        this.hasRemindAll = true
                        this.hasNotSubmitDialog.visible = false
                        const alertDialog = this.$bkInfo({
                            type: 'success',
                            title: res.message,
                            showFooter: false
                        })
                        setTimeout(() => {
                            alertDialog.close()
                        }, 500)
                    }
                })
            },
            // 打开日报详情
            openDialog (daily) {
                this.dialogMember = daily
                this.daliyDetailDialog.visible = true
            },
            // 提交我的点评信息
            submitMyComment (dialogMember) {
                if (this.myComment.length) {
                    const alertDialog = this.$bkInfo({
                        type: 'success',
                        title: '点评成功',
                        showFooter: false
                    })
                    // 发送请求，将我的点评提交给后台
                    this.$http.post('/evaluate_daliy/', { daily_id: dialogMember.id, evaluate_content: this.myComment }).then(res => {
                        if (res.message) {
                            setTimeout(() => {
                                alertDialog.close()
                            }, 500)
                            this.daliyDetailDialog.visible = false
                        } else {
                            return false
                        }
                    })
                    setTimeout(() => {
                        alertDialog.close()
                    }, 500)
                }
                this.daliyDetailDialog.visible = false
            },
            // 封装getdata请求
            getdata (params) {
                this.$http.get('/list_member_daily/', params).then(res => {
                    this.hasSubmitDaily = res.hasdaliy
                    this.hasNotSubmitMember = res.nodaliy
                })
            },
            // 改变日历的日期
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                // 发送请求，获取选定日期的信息
                this.getdata({ params: { group_id: this.selectGroupId, time: this.formatDate } })
            },
            // 改变当前查看组
            changeGroup (selectGroupId) {
                this.selectGroupId = selectGroupId
                // 发送请求，获取选定组的信息
                this.getdata({ params: { group_id: this.selectGroupId, time: this.formatDate } })
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
