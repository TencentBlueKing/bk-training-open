<template>
    <div class="excellentdaily">
        <div class="excellentdaily-btn">
            <div class="bk-button-group">
                <bk-button size="small" :class="selectType === 'all' ? 'is-selected' : ''" @click="changeType('all')">全部</bk-button>
                <bk-button size="small" :class="selectType === 'month' ? 'is-selected' : ''" @click="changeType('month')">日期</bk-button>
            </div>
            <div class="excellentdaily-date-select" v-show="selectType === 'month'">
                <bk-date-picker :options="customOption" type="month" @change="changeDate" style="width: 250px;" :clearable="false" behavior="normal" font-size="normal" v-model="curDateTime"></bk-date-picker>
                <FastBtn :time="time" @topItem="topItem" @bottomItem="bottomItem" />
            </div>
            <!-- 分割线 -->
            <div class="halving"></div>
        </div>
        <!-- 渲染的内容 -->
        <div class="excellentdaily-renderlistbox" v-show="renderDaily && renderDaily.length">
            <bk-card class="all-report-card card"
                v-for="(daily, index) in renderDaily"
                :key="index"
                :title="daily.create_by + '(' + (daily.create_name) + ')'">
                <div class="card-header" slot="header" :title="daily.create_by + '(' + (daily.create_name) + ')'">
                    <div :class="isadmin ? 'card-header-basic' : 'card-header-basic-noadmin'">
                        <div class="card-usename">{{daily.create_by + '(' + (daily.create_name) + ')'}}</div>
                        <div class="card-time">
                            <div>{{daily.date}}</div>
                        </div>
                    </div>
                    <div class="setgood-box" v-show="isadmin" @click="setgoodDaily(daily)">
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
            <div class="renderlistbox-pagination">
                <bk-pagination
                    size="small"
                    @change="changePage"
                    @limit-change="changeLimit"
                    :current.sync="pagingDevice.curPage"
                    :limit="pagingDevice.limit"
                    :count=" pagingDevice.count || 8"
                    :location="pagingDevice.location"
                    :align="pagingDevice.align"
                    :show-limit="pagingDevice.showLimit"
                    :limit-list="pagingDevice.limitList">
                </bk-pagination>
            </div>
        </div>
        <div class="notrender" v-show="renderDaily && renderDaily.length === 0">
            <div class="exception-wrap">
                <bk-exception :options="customOption" ext-cls="notrender-box" class="exception-wrap-item exception-part" type="empty" scene="part" :class="{ 'exception-gray': isGray }"> 暂时还没有优秀日报 </bk-exception>
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { bkPagination, bkButton } from 'bk-magic-vue'
    import { isAdmin } from '@/utils/index.js'
    import FastBtn from '@/components/GroupDailys/FastBtn'
    import requestApi from '@/api/request.js'
    const { getGoodDaily, setGoodDaily } = requestApi
    export default {
        components: {
            bkButton,
            bkPagination,
            FastBtn
        },
        props: {
            curgroupid: {
                type: Number
            },
            adminlist: {
                type: Object
            }
        },
        data () {
            return {
                isadmin: false,
                tabBtnContent: ['全部', '日期'],
                myMsg: JSON.parse(window.localStorage.getItem('userMsg')),
                // 当前选中的类型  默认是all,month
                selectType: 'all',
                // 当前选中的日期
                curDateTime: moment(new Date((new Date().getTime() - 24 * 60 * 60 * 1000))).format('YYYY-MM-DD'),
                // 渲染的数据
                renderDaily: [],
                // 分页设置
                pagingDevice: {
                    curPage: 1,
                    limit: 8,
                    count: 300,
                    location: 'left',
                    align: 'right',
                    showLimit: true,
                    limitList: [8, 16, 32, 64]
                },
                // 日期禁用
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                // 快捷组件按钮的禁用情况
                time: true
            }
        },
        watch: {
            curgroupid () {
                this.pagingDevice.curPage = 1
                this.RenderData()
            },
            adminlist (oldVal) {
                this.isadmin = isAdmin(this.myMsg.username, oldVal)
            }
        },
        activated () {
            this.initData()
            this.isadmin = isAdmin(this.myMsg.username, this.adminlist)
        },
        methods: {
            // 快捷切换(上)
            topItem () {
                if (this.selectType === 'month') {
                    this.curDateTime = moment(this.curDateTime).subtract(1, 'month').format('YYYY-MM')
                    this.changeDate(this.curDateTime)
                    this.time = false
                }
            },
            // 快捷切换(下)
            bottomItem () {
                if (this.selectType === 'month' && moment(this.curDateTime).add(1, 'month').format('YYYY-MM') <= moment(new Date()).format('YYYY-MM')) {
                    this.curDateTime = moment(this.curDateTime).add(1, 'month').format('YYYY-MM')
                    this.changeDate(this.curDateTime)
                }
                if (this.selectType === 'month' && moment(this.curDateTime).format('YYYY-MM') === moment(new Date()).format('YYYY-MM')) {
                    this.time = true
                }
            },
            // 初始化调用
            initData () {
                this.RenderData()
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
            // 类型的改变
            changeType (type) {
                this.pagingDevice.curPage = 1
                this.selectType = type
                this.RenderData()
            },
            // 日期改变
            changeDate (date) {
                this.time = false
                this.pagingDevice.curPage = 1
                this.curDateTime = moment(date).format('YYYY-MM')
                this.RenderData()
            },
            // 切换页码
            changePage (curPage) {
                this.pagingDevice.curPage = curPage
                this.RenderData()
            },
            // 分页尺寸的变化
            changeLimit (curlimit) {
                this.pagingDevice.curPage = 1
                this.pagingDevice.limit = curlimit
                this.RenderData()
            },
            // 设为优秀日报(设置优秀和取消优秀)
            setgoodDaily (item) {
                setGoodDaily(this.curgroupid, item.id).then(res => {
                    if (res.code !== -1) {
                        this.handleSuccess('取消优秀')
                        this.RenderData()
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
            // 渲染数据的设置
            RenderData (year = '', month = '') {
                const { curPage, limit } = this.pagingDevice
                // 按什么类型搜索
                if (this.selectType === 'month') {
                    year = moment(this.curDateTime).format('YYYY')
                    month = moment(this.curDateTime).format('MM')
                }
                getGoodDaily(this.curgroupid, this.selectType, curPage, limit, year, month).then(res => {
                    this.renderDaily = res.data.daily_list
                    this.pagingDevice.count = res.data.total_num
                })
            }
        }
    }
</script>

<style src='./index.css' scoped ></style>
