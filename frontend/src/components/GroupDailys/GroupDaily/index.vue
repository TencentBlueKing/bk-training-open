<template>
    <div class="groupdaily">
        <div class="groupdaily-btn">
            <div class="bk-button-group">
                <bk-button :class="curType === 'date' ? 'is-selected' : ''" size="small" @click="selectedType('date')">日期</bk-button>
                <bk-button :class="curType === 'member' ? 'is-selected' : ''" size="small" @click="selectedType('member')">成员</bk-button>
            </div>
            <!-- 成员选择器 -->
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
                    <bk-option v-for="option in groupusers"
                        :key="option.id"
                        :id="option.id"
                        :name="option.username + '(' + option.name + ')'">
                    </bk-option>
                </bk-select>
                <FastBtn :top="top" :bottom="bottom" @topItem="topItem" @bottomItem="bottomItem" />
            </div>
            <!-- 日期选择器 -->
            <div class="groupdaily-date-select" v-show="curType === 'date'">
                <bk-date-picker font-size="normal" :options="customOption" @change="changeDate" style="width: 250px;" :clearable="false" v-model="curDateTime"></bk-date-picker>
                <FastBtn :time="time" @topItem="topItem" @bottomItem="bottomItem" />
            </div>
            <!-- 分割线 -->
            <div class="halving"></div>
        </div>
        <!-- 渲染的内容 -->
        <div class="renderlistbox" v-show="renderDaily && renderDaily.length">
            <bk-card class="all-report-card card"
                v-for="(daily, index) in renderDaily"
                :key="index"
                :title="daily.create_by + '(' + (daily.create_name) + ')'">
                <div class="card-header" slot="header" :title="daily.create_by + '(' + (daily.create_name) + ')'">
                    <div class="card-usename">{{daily.create_by + '(' + (daily.create_name) + ')'}}</div>
                    <div class="card-time">
                        <div>{{daily.date}}</div>
                    </div>
                    <div class="setgood-box" @click="setgoodDaily(daily)">
                        {{daily.is_perfect ? '取消优秀' : '设为优秀'}}
                    </div>
                </div>
                <div v-for="(dailyContnet, innerIndex) in daily.content" :key="innerIndex">
                    <div class="sub-title">{{dailyContnet.title}}</div>
                    <div v-if="dailyContnet.type === 'table'" style="font-size: 14px">
                        <div v-for="(row, iiIndex) in dailyContnet.content" :key="iiIndex">
                            <div class="card-pre">
                                <div class="content-wapper">
                                    <span class="time-wapper">
                                        <bk-tag v-show="(myMsg.username === daily.create_by || !row.isPrivate) && judgeFloatString(row.cost)">
                                            {{typeof row.cost === 'string' ? row.cost : row.cost.toFixed(1) + 'h'}}
                                        </bk-tag>
                                        <bk-tag v-show="!(myMsg.username === daily.create_by || !row.isPrivate) || !judgeFloatString(row.cost)">
                                            - -
                                        </bk-tag>
                                    </span>
                                    {{row.text}}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="font-size:14px;line-height: 22px;" v-else>
                        {{dailyContnet.text}}
                    </div>
                </div>
            </bk-card>
            <li class="renderlistbox-tiptoe" v-for="item in [1,2,3,4]" :key="item"></li>
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
    import FastBtn from '@/components/GroupDailys/FastBtn'
    import { bkSelect, bkOption, bkDatePicker, bkException, bkPagination, bkButton } from 'bk-magic-vue'
    import requestApi from '@/api/request.js'
    import { isAdmin } from '@/utils/index.js'
    const { getDaily, setGoodDaily } = requestApi
    export default {
        components: {
            bkSelect,
            bkOption,
            bkDatePicker,
            bkException,
            bkPagination,
            bkButton,
            FastBtn
        },
        props: {
            // 当前组id
            curgroupid: {
                type: Number
            },
            adminlist: {
                type: Object
            },
            groupusers: {
                type: Object
            },
            curdate: {
                type: String
            },
            username: {
                type: String
            }
        },
        data (s) {
            return {
                isfirstEnter: true,
                isadmin: false,
                myMsg: JSON.parse(window.localStorage.getItem('userMsg')),
                // 当前选中的类比
                curType: 'date',
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
                },
                // 一天的毫秒数
                dayMsec: 24 * 60 * 60 * 1000,
                // 快捷组件按钮的禁用情况 time(时间上限) / all / top / bottom / true
                top: true,
                bottom: false,
                time: false,
                // 当前快捷用户的下标位置
                forbUserIndex: 0
            }
        },
        watch: {
            groupusers (oldVal) {
                if (oldVal.length === 0 || oldVal.length === 1) {
                    this.top = true
                    this.bottom = true
                }
                this.filterUserId(this.username).then(res => {
                    this.curSelectUser = res
                    this.selectedType('member', true)
                })
            },
            curgroupid () {
                // 如果用户组发生了变化开始
                this.curType = 'date'
                this.pagingDevice.curPage = 1
                this.changeDate(moment(this.curDateTime).format('YYYY-MM-DD'))
            },
            curdate (oldVal) {
                this.curDateTime = oldVal
                this.changeDate(oldVal)
            },
            curSelectUser (oldVal) {
                this.selectUserIndex()
            },
            adminlist (oldVal) {
                this.isadmin = isAdmin(this.myMsg.username, oldVal)
            }
        },
        activated () {
            // 切换回来会又新数据第一次不执行
            if (!this.isfirstEnter) {
                this.selectedType(this.curType)
            }
            this.isfirstEnter = false
        },
        methods: {
            // 快捷切换(上)
            topItem () {
                if (this.curType === 'date') {
                    this.curDateTime = moment(this.curDateTime).subtract(1, 'days').format('YYYY-MM-DD')
                    this.changeDate(this.curDateTime)
                    this.time = false
                }
                // member
                if (this.curType === 'member') {
                    this.selectUserIndex()
                    if (this.forbUserIndex === 0) {
                        // 灰色
                        this.top = true
                    } else {
                        this.curSelectUser = this.groupusers[this.forbUserIndex - 1].id
                        this.changeUser(this.groupusers[this.forbUserIndex - 1].id)
                        this.top = false
                    }
                    this.bottom = false
                }
            },
            // 快捷切换(下)
            bottomItem () {
                if (this.curType === 'date' && moment(this.curDateTime).add(1, 'days').format('YYYY-MM-DD') <= moment(new Date()).format('YYYY-MM-DD')) {
                    this.curDateTime = moment(this.curDateTime).add(1, 'days').format('YYYY-MM-DD')
                    this.changeDate(this.curDateTime)
                }
                if (this.curType === 'date' && moment(this.curDateTime).format('YYYY-MM-DD') === moment(new Date()).format('YYYY-MM-DD')) {
                    this.time = true
                }
                // member
                if (this.curType === 'member') {
                    this.selectUserIndex()
                    if (this.forbUserIndex === this.groupusers.length - 1) {
                        // 灰色
                        this.bottom = true
                    } else {
                        this.curSelectUser = this.groupusers[this.forbUserIndex + 1].id
                        this.changeUser(this.groupusers[this.forbUserIndex + 1].id)
                        this.bottom = false
                    }
                    this.top = false
                }
            },
            // 日期改变
            changeDate (date, flat = true) {
                if (flat) {
                    this.time = false
                }
                this.getRenderDaily(moment(date).format('YYYY-MM-DD'), '', this.pagingDevice.limit, this.pagingDevice.curPage)
            },
            // 成员的改变
            changeUser (id) {
                this.pagingDevice.curPage = 1
                this.getRenderDaily('', id, this.pagingDevice.limit, this.pagingDevice.curPage)
            },
            // 切换 日期或者人名
            selectedType (type, flat = false) {
                this.pagingDevice.curPage = 1
                // 跟换焦点
                this.curType = type
                // 切换到了用户 找第一个默认用户的日报(全部)
                if (type === 'member') {
                    if (this.groupusers.length !== 0) {
                        if (flat) {
                            // 链接跳进来
                            this.changeUser(this.curSelectUser)
                        } else {
                            // 不是链接跳进来
                            this.curSelectUser = this.groupusers[0].id
                            this.changeUser(this.curSelectUser)
                        }
                    } else {
                        // 没成员就空
                        this.curSelectUser = ''
                    }
                } else {
                    // 找当前时间的日报
                    this.changeDate(this.curDateTime, false)
                }
            },
            // 切换页码
            changePage (curPage) {
                this.pagingDevice.curPage = curPage
                this.getRenderDaily('', this.curSelectUser, this.pagingDevice.limit, curPage)
            },
            // 分页尺寸的变化
            changeLimit (curlimit) {
                this.pagingDevice.curPage = 1
                this.pagingDevice.limit = curlimit
                this.getRenderDaily('', this.curSelectUser, this.pagingDevice.limit, 1)
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
            // 当前用户在数组的哪个地方
            selectUserIndex () {
                this.groupusers.forEach((item, index) => {
                    if (item.id === this.curSelectUser) {
                        this.forbUserIndex = index
                        if (index === 0) {
                            this.top = true
                            this.bottom = false
                        }
                        if (index === this.groupusers.length - 1) {
                            this.top = false
                            this.bottom = true
                        }
                        if (index !== 0 && index !== this.groupusers.length - 1) {
                            this.top = false
                            this.bottom = false
                        }
                    }
                })
            },
            // 根据用户名过滤出用户id
            filterUserId (username) {
                return new Promise((resolve, reject) => {
                    this.groupusers.forEach(item => {
                        if (item.username === username) {
                            resolve(item.id)
                        }
                    })
                })
            },
            // 设为优秀日报(设置优秀和取消优秀)
            setgoodDaily (item) {
                setGoodDaily(this.curgroupid, item.id).then(res => {
                    if (res.code !== -1) {
                        item.is_perfect = !item.is_perfect
                        if (item.is_perfect === true) {
                            this.handleSuccess('置为优秀')
                        } else {
                            this.handleSuccess('取消优秀')
                        }
                    } else {
                        this.handleSuccess('没有管理员权限', 'error')
                    }
                })
            },
            handleSuccess (msg, type = 'success') {
                const config = {
                    message: msg,
                    offsetY: 80,
                    theme: type
                }
                this.$bkMessage(config)
            },
            /*
                获得渲染日报数据
                移除为 组id、当前选中的日期、当前选中的用户、分页限制、当前页
            */
            getRenderDaily (curDate, curUserId, limit, curPage) {
                getDaily(this.curgroupid, curDate, curUserId, limit, curPage).then(res => {
                    this.renderDaily = res.data.reports.filter(item => !this.adminlist.includes(item.create_by))
                    this.pagingDevice.count = res.data.total_report_num
                    this.my_today_report = res.data.total_report_num
                })
            }
        }
    }
</script>

<style src='./index.css' scoped></style>
