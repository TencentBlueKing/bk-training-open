<template>
    <div class="groupdaily">
        <div class="groupdaily-btn">
            <div class="bk-button-group">
                <bk-button :class="curType === 'date' ? 'is-selected' : ''" size="small" @click="selectedType('date')">日期</bk-button>
                <bk-button :class="curType === 'member' ? 'is-selected' : ''" size="small" @click="selectedType('member')">成员</bk-button>
            </div>
            <!-- 成员选择器或者日期选择器 -->
            <div class="groupdaily-member-select" v-show="curType === 'member'">
                <bk-select
                    :disabled="false"
                    v-model="curSelectUser"
                    style="width: 250px;"
                    behavior="normal"
                    :clearable="false"
                    font-size="normal"
                    @selected="changeUser"
                    ext-popover-cls="select-popover-custom"
                    searchable>
                    <bk-option v-for="option in groupUsers"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name || option.username">
                    </bk-option>
                </bk-select>
            </div>
            <div class="groupdaily-date-select" v-show="curType === 'date'">
                <bk-date-picker font-size="normal" :options="customOption" @change="changeDate" style="width: 250px;" :clearable="false" class="mr15" v-model="curDateTime"></bk-date-picker>
            </div>
        </div>
        <!-- 渲染的内容 -->
        <div class="renderlistbox" v-show="renderDaily && renderDaily.length">
            <bk-card class="all-report-card card"
                v-for="(daily, index) in renderDaily"
                :key="index"
                :title="daily.create_by + '(' + (daily.create_name) + ')'">
                <div class="card-header" slot="header" :title="daily.create_by + '(' + (daily.create_name) + ')'">
                    <span class="card-usename">{{daily.create_by + '(' + (daily.create_name) + ')'}}</span>
                    <span class="card-time">{{daily.date}}</span>
                </div>
                <div v-for="(dailyContnet, innerIndex) in daily.content" :key="innerIndex">
                    <div class="sub-title">{{dailyContnet.title}}</div>
                    <div v-if="dailyContnet.type === 'table'" style="font-size: 14px">
                        <div v-for="(row, iiIndex) in dailyContnet.content" :key="iiIndex">
                            <pre class="card-pre">
                                            <div class="content-wapper">
                                                <span class="time-wapper">
                                                    <bk-tag v-show="(myMsg.username === daily.create_by || !row.isPrivate) && judgeFloatString(row.cost)" theme="info">
                                                        {{typeof row.cost === 'string' ? row.cost : row.cost.toFixed(1) + 'h'}}
                                                    </bk-tag>
                                                    <bk-tag v-show="!(myMsg.username === daily.create_by || !row.isPrivate) || !judgeFloatString(row.cost)" theme="info">
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
            </bk-card>
            <!-- 分页器 -->
            <div class="renderlistbox-pagination" v-show="curType === 'member'">
                <bk-pagination
                    size="small"
                    @change="changePage"
                    @limit-change="changeLimit"
                    :current.sync="pagingDevice.curPage"
                    :limit="pagingDevice.limit"
                    :count="pagingDevice.count"
                    :location="pagingDevice.location"
                    :align="pagingDevice.align"
                    :show-limit="pagingDevice.showLimit"
                    :limit-list="pagingDevice.limitList">
                </bk-pagination>
            </div>
        </div>
        <div class="notrender" v-show="renderDaily && renderDaily.length === 0">
            <div class="exception-wrap">
                <bk-exception ext-cls="notrender-box" class="exception-wrap-item exception-part" type="empty" scene="part" :class="{ 'exception-gray': isGray }"> 暂时还没有日报 </bk-exception>
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { bkSelect, bkOption, bkDatePicker, bkException, bkPagination, bkButton } from 'bk-magic-vue'
    import requestApi from '@/api/request.js'
    const { getGroupUsers, getDaily } = requestApi
    export default {
        components: {
            bkSelect,
            bkOption,
            bkDatePicker,
            bkException,
            bkPagination,
            bkButton
        },
        data (s) {
            return {
                myMsg: JSON.parse(window.localStorage.getItem('userMsg')),
                // 当前组id
                curGroupID: '',
                // 当前选中的类比
                curType: 'date',
                // 当前小组的全部成员数据
                groupUsers: [],
                curSelectUser: null,
                // 当前选中的日期
                curDateTime: moment(new Date((new Date().getTime() - 24 * 60 * 60 * 1000))).format('YYYY-MM-DD'),
                // 渲染的日报数据
                renderDaily: [],
                // 分页设置
                pagingDevice: {
                    curPage: 1,
                    limit: 8,
                    count: 0,
                    location: 'left',
                    align: 'right',
                    showLimit: true,
                    limitList: [8, 16, 32, 64]
                },
                isGray: false,
                // 日期禁用
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                }

            }
        },
        computed: {
            checkUser () {
                return this.$store.state.groupDaily.selectUserId
            },
            curGroupIDChange () {
                return this.$store.state.groupDaily.curGroupID
            }
        },
        watch: {
            curGroupIDChange (oldVal) {
                this.curGroupID = oldVal
                // 只要Vuex的组ID变动 组成员就重新获取
                this.getAllGroupUsers(true)
                // 如果用户组发生了变化开始
                this.curType = 'date'
                this.changeDate(moment(new Date((new Date().getTime() - 24 * 60 * 60 * 1000))).format('YYYY-MM-DD'))
            },
            checkUser (oldVal) {
                this.curSelectUser = oldVal
                this.selectedType('member')
            }
        },
        methods: {
            // 初始化调用
            activated () {
                this.curGroupID = this.$store.state.groupDaily.curGroupID
                this.getAllGroupUsers(true)
                this.curType = 'date'
                this.changeDate(moment(new Date((new Date().getTime() - 24 * 60 * 60 * 1000))).format('YYYY-MM-DD'))
            },
            // 获得当前组的组成员 并且选中第一个人
            getAllGroupUsers (flat) {
                getGroupUsers(this.curGroupID).then(res => {
                    this.groupUsers = res.data
                    // 如果是成员默认展示第一个人
                    if (flat) {
                        this.curSelectUser = res.data[0].id
                    }
                })
            },
            // 日期改变
            changeDate (date) {
                this.getRenderDaily(moment(date).format('YYYY-MM-DD'), '', this.pagingDevice.limit, this.pagingDevice.curPage).then(res => {
                    this.renderDaily = res
                })
            },
            // 成员的改变
            changeUser (id) {
                this.pagingDevice.curPage = 1
                this.getRenderDaily('', id, this.pagingDevice.limit, this.pagingDevice.curPage).then(res => {
                    this.renderDaily = res
                })
            },
            // 切换 日期或者人名
            selectedType (type) {
                this.pagingDevice.curPage = 1
                // 跟换焦点
                this.curType = type
                // 切换到了用户 找第一个默认用户的日报(全部)
                if (type === 'member') {
                    this.changeUser(this.curSelectUser)
                } else {
                    // 找当前时间的日报
                    this.changeDate(this.curDateTime)
                }
            },
            // 切换页码
            changePage (curPage) {
                this.pagingDevice.curPage = curPage
                this.getRenderDaily('', this.curSelectUser, this.pagingDevice.limit, curPage).then(res => {
                    this.renderDaily = res
                })
            },
            // 分页尺寸的变化
            changeLimit (curlimit) {
                this.pagingDevice.curPage = 1
                this.pagingDevice.limit = curlimit
                this.getRenderDaily('', this.curSelectUser, this.pagingDevice.limit, 1).then(res => {
                    this.renderDaily = res
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
            /*
                获得渲染日报数据
                移除为 组id、当前选中的日期、当前选中的用户、分页限制、当前页
            */
            getRenderDaily (curDate, curUserId, limit, curPage) {
                return new Promise((resolve, reject) => {
                    getDaily(this.curGroupID, curDate, curUserId, limit, curPage).then(res => {
                        this.pagingDevice.count = res.data.total_report_num
                        this.my_today_report = res.data.my_today_report
                        resolve(res.data.reports)
                    })
                })
            }
        }
    }
</script>

<style src='./index.css' scoped></style>
