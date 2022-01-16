<template>
    <div class="groupDailys">
        <div class="groupDailys-btn">
            <div><bk-select
                :disabled="false"
                v-model="selectGroup"
                @selected="changeGroup"
                style="width: 250px;"
                ext-cls="selectgroup"
                :clearable="false"
                behavior="simplicity"
                searchable>
                <bk-option v-for="option in groupList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select></div>
            <bk-button class="top-container-right-btn" :hover-theme="'primary'" @click="clicktimeManage">
                空闲时间管理
            </bk-button>
        </div>
        <bk-sideslider
            width="400"
            :is-show.sync="timeSetting.visible"
            :quick-close="true"
            @hidden="hiddenSlider"
            direction="right"
            ext-cls="time-slide">
            <div slot="header" class="slide-header">
                <div :class="{
                    'header-tabs': true,
                    'tabs-active': title === activeTabTitle
                }" v-for="(title,tindex) in slideTitleList" :key="tindex" @click="changeTab(title)">
                    {{title}}
                </div>
            </div>
            <div slot="content">
                <div class="time-body" style="height: 530px;padding: 30px 0 0 10px;" v-show="activeTabTitle === slideTitleList[0]">
                    <div class="time-apply">
                        <bk-form label-width="100">
                            <bk-form-item label="日期" label-width="70">
                                <bk-date-picker class="mr15" :options="options" v-model="addTimeDialog.data.date" placeholder="起始日期" />
                            </bk-form-item>
                            <bk-form-item label="起始时间">
                                <bk-time-picker class="mr15" format="HH:mm" :editable="false" :enter-mode="false" v-model="addTimeDialog.data.startTime" placeholder="起始时间" />
                            </bk-form-item>
                            <bk-form-item label="结束时间">
                                <bk-time-picker class="mr15" format="HH:mm" :editable="false" :enter-mode="false" v-model="addTimeDialog.data.endTime" placeholder="结束时间" />
                            </bk-form-item>
                        </bk-form>
                        <bk-button :hover-theme="'primary'" @click="doAddTime" style="margin-left: 290px;margin-top: 20px;">增加</bk-button>
                    </div>
                </div>
                <div class="time-body" style="padding: 30px 10px 0;" v-show="activeTabTitle === slideTitleList[1]">
                    <div class="time-manage">
                        <bk-form label-width="100">
                            <bk-form-item label="起始日期">
                                <bk-date-picker class="mr15" v-model="startTime" placeholder="起始日期" @change="loadUserTime" />
                            </bk-form-item>
                            <bk-form-item label="结束日期">
                                <bk-date-picker class="mr15" v-model="endTime" placeholder="结束日期" @change="loadUserTime" />
                            </bk-form-item>
                        </bk-form>
                        <bk-table
                            v-show="true"
                            style="margin-top:30px;"
                            :virtual-render="false"
                            :data="timeData"
                            :size="timeTableData.size"
                            :outer-border="false"
                            :header-border="false"
                            :header-cell-style="{ background: '#fff' }"
                            @page-change="handlePageChange"
                            @page-limit-change="handlePageLimitChange">
                            <div slot="empty-text">
                                空数据
                            </div>
                            <bk-table-column label="日期" prop="date" min-width="50" margin-top="55px" show-overflow-tooltip="true"></bk-table-column>
                            <bk-table-column label="空闲时间" prop="free_time" min-width="50" show-overflow-tooltip="true"></bk-table-column>
                            <bk-table-column label="操作" width="100">
                                <template slot-scope="props">
                                    <bk-button theme="warning" text @click="showChangeTime(props.row)">修改</bk-button>
                                    <bk-button theme="danger" text @click="removeTime(props.row)">移除</bk-button>
                                </template>
                            </bk-table-column>
                        </bk-table></div>
                    <bk-dialog v-model="changeTimeDialog.visible" render-directive="if" theme="primary" title="修改空闲时间" class="add-time-dialog" @confirm="doChangeTime">
                        <bk-form label-width="80">
                            <bk-form-item label="日期">
                                <bk-date-picker class="mr15" :options="options" v-model="changeTimeDialog.data.date" placeholder="起始日期" />
                            </bk-form-item>
                            <bk-form-item label="起始时间">
                                <bk-time-picker class="mr15" format="HH:mm" :editable="false" :enter-mode="false" v-model="changeTimeDialog.data.startTime" placeholder="起始时间" />
                            </bk-form-item>
                            <bk-form-item label="结束时间">
                                <bk-time-picker class="mr15" format="HH:mm" :editable="false" :enter-mode="false" v-model="changeTimeDialog.data.endTime" placeholder="结束时间" />
                            </bk-form-item>
                        </bk-form>
                    </bk-dialog>
                </div>
            </div>
        </bk-sideslider>
        <keep-alive>
            <component :is="curComponents" :curgroupid="selectGroup" :groupusers="renderUser" :username="username" :refreshpage="refreshPage"></component>
        </keep-alive>
    </div>
</template>

<script>
    import { bkSelect, bkOption } from 'bk-magic-vue'
    import TabBtn from '@/components/TabBtn/index.vue'
    import TimeSchedule from '@/components/TimeSchedules/TimeSchedule'
    import requestApi from '@/api/request.js'
    import moment from 'moment'
    const { getallGroups, getGroupUsers } = requestApi
    export default {
        components: {
            bkSelect,
            bkOption,
            TabBtn,
            TimeSchedule
        },
        data () {
            return {
                // 当前选中的组
                selectGroup: '',
                // 当前活着的组件
                curComponents: 'TimeSchedule',
                // 用户
                renderUser: null,
                curDate: new Date(),
                timeSetting: {
                    visible: false
                },
                istimeTableLoad: true,
                timeTableData: {
                    size: 'small',
                    data: [],
                    isAdmin: false
                },
                timeFormData: {
                    reason: '',
                    dateTimeRange: [new Date(), new Date()]
                },
                slideTitleList: [
                    '新增空闲时间',
                    '查看空闲时间'
                ],
                activeTabTitle: '新增空闲时间',
                groupList: [],

                selectedGroup: -1,
                curUsertimeList: [],
                loading: true,
                startTime: new Date(),
                endTime: moment(new Date()).add(6, 'days').format('YYYY-MM-DD'),
                changeMemberId: '',
                timeData: [],
                addTimeDialog: {
                    visible: false,
                    data: {
                        date: new Date(),
                        startTime: '08:00:00',
                        endTime: '22:00:00'
                    }
                },
                changeTimeDialog: {
                    visible: false,
                    data: {
                        date: new Date(),
                        startTime: '08:00:00',
                        endTime: '22:00:00'
                    }
                },
                options: {
                    disabledDate: (date) => {
                        return date < moment(new Date()).subtract('1', 'days')
                    }
                },
                // 新增和删除成功刷新当前页面
                refreshPage: false
            }
        },
        watch: {
            selectGroup () {
                this.renderUserList()
            }
        },
        created () {
            getallGroups().then(res => {
                this.selectGroup = res.data[0].id
                this.groupList = res.data
                this.takeGroupuser()
            })
        },
        methods: {
            // 请假滑窗关闭事件
            hiddenSlider () {
                this.timeFormData.reason = ''
                this.timeFormData.dateTimeRange = [new Date(), new Date()]
                this.activeTabTitle = '新增空闲时间'
            },
            // 请假管理按钮点击事件
            clicktimeManage () {
                this.timeSetting.visible = true
            },
            // 切换请假页签事件
            changeTab (title) {
                this.activeTabTitle = title
                if (title === '查看空闲时间') {
                    this.loadUserTime()
                }
            },
            changeGroup (val) {
                this.selectGroup = val
            },
            // 获取组所有用户
            renderUserList () {
                getGroupUsers(this.selectGroup).then(res => {
                    this.renderUser = res.data
                })
            },
            // 跳转到的 组下的人
            takeGroupuser () {
                // 跳转过来的
                if (this.$route.query.group !== undefined && this.$route.query.username !== undefined) {
                    this.selectGroup = this.$route.query.group
                    this.username = this.$route.query.username
                }
                if (this.$route.query.group !== undefined && this.$route.query.date !== undefined) {
                    this.selectGroup = this.$route.query.group
                    this.date = this.$route.query.date
                }
            },
            loadUserTime () {
                this.loading = true
                const startDate = moment(this.startTime).format(moment.HTML5_FMT.DATE)
                const endDate = moment(this.endTime).format(moment.HTML5_FMT.DATE)
                this.$http.get(
                    '/free_time/?start_date=' + startDate + '&end_date=' + endDate
                ).then(res => {
                    if (res.result) {
                        this.timeData = res.data
                        for (const timeData of this.timeData) {
                            timeData.free_time = moment(timeData.start_time).format('HH:mm') + '-' + moment(timeData.end_time).format('HH:mm')
                        }
                    } else {
                        this.$bkMessage({
                            theme: 'warning',
                            message: res.message
                        })
                    }
                }).finally(() => {
                    setTimeout(() => {
                        this.loading = false
                    }, 600)
                })
            },
            showChangeTime (row) {
                this.changeTimeDialog.data = {
                    date: new Date(),
                    startTime: '08:00',
                    endTime: '22:00'
                }
                this.changeMemberId = row.id
                this.changeTimeDialog.visible = true
            },
            doChangeTime (row) {
                this.changeTimeDialog.visible = false
                this.loading = true
                const date = moment(this.changeTimeDialog.data.date).format('YYYY-MM-DD')
                this.$http.patch(
                    '/free_time/' + this.changeMemberId + '/',
                    {
                        'new_start_date': date + ' ' + this.changeTimeDialog.data.startTime.slice(0, 5),
                        'new_end_date': date + ' ' + this.changeTimeDialog.data.endTime.slice(0, 5)
                    },
                    { 'emulateJSON': true }
                ).then(res => {
                    if (res.result) {
                        this.$bkMessage({
                            theme: 'success',
                            message: res.message
                        })
                        this.loadUserTime()
                    } else {
                        this.$bkMessage({
                            theme: 'warning',
                            message: res.message
                        })
                        this.loading = false
                    }
                })
                this.refreshPage = !this.refreshPage
            },
            removeTime (row) {
                this.loading = true
                this.$http.delete(
                    '/free_time/' + row.id + '/'
                ).finally(() => {
                    this.loadUserTime()
                })
                this.refreshPage = !this.refreshPage
            },
            showAddTime () {
                this.addTimeDialog.data = {
                    date: new Date(),
                    startTime: '08:00',
                    endTime: '22:00'
                }
                this.addTimeDialog.visible = true
            },
            doAddTime () {
                this.addTimeDialog.visible = false
                this.loading = true
                const date = moment(this.addTimeDialog.data.date).format('YYYY-MM-DD')
                const data = {
                    free_times: [
                        {
                            start_time: date + ' ' + this.addTimeDialog.data.startTime,
                            end_time: date + ' ' + this.addTimeDialog.data.endTime
                        }
                    ]
                }
                this.$http.post(
                    '/free_time/',
                    data
                ).then(res => {
                    if (res.result) {
                        this.$bkMessage({
                            theme: 'success',
                            message: res.message
                        })
                        this.loadUserTime()
                    } else {
                        this.$bkMessage({
                            theme: 'warning',
                            message: res.message
                        })
                        this.loading = false
                    }
                })
                this.refreshPage = !this.refreshPage
            }
        }
    }
</script>

<style >
    @import url('./index.css');
</style>
