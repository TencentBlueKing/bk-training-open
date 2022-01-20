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
                    <bk-dropdown-menu :align="'right'" v-show="isadmin">
                        <template slot="dropdown-trigger">
                            <span class="dropdown-trigger-btn bk-icon icon-cog-shape"><span>
                            </span></span></template>
                        <ul class="bk-dropdown-list" slot="dropdown-content">
                            <li @click="setgoodDaily(daily)"><a href="javascript:;">{{daily.is_perfect ? '取消优秀' : '设为优秀'}}</a></li>
                            <li @click="chooseEvaluate(daily)"><a href="javascript:;">评价日报</a></li>
                        </ul>
                    </bk-dropdown-menu>
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
                <!-- 管理员评价 -->
                <div v-if=" daily.evaluate.length !== 0">
                    <div class="evaluation">
                        <div class="sub-title">管理员评价</div>
                    </div>
                    <!-- 评价的内容和管理员 -->
                    <div style="font-size: 14px" class="comment">
                        <div v-for="(row, iiIndex) in daily.evaluate" :key="iiIndex">
                            <div class="card-pre" v-if="row.evaluate !== ''">
                                <div class="content-wapper">
                                    <bk-tag>
                                        {{row.name}}
                                    </bk-tag>
                                    <span>{{row.evaluate}}</span>
                                </div>
                            </div>
                        </div>
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
        <!-- 弹出 -->
        <bk-dialog
            :value="isshowDlog"
            theme="primary"
            :mask-close="false"
            :header-position="left"
            :auto-close="false"
            @confirm="dialogConfirm()"
            @cancel="dialogCancel()"
            :title="isdiscussdaily ? '评论修改' : '新增评论'"
            class="group-dialog"
        >
            <bk-input
                placeholder="清空默认为删除该条评论"
                :type="'textarea'"
                :rows="3"
                :maxlength="200"
                v-model="discussContent">
            </bk-input>
        </bk-dialog>
    </div>
</template>

<script>
    import moment from 'moment'
    import { bkPagination, bkButton, bkInput } from 'bk-magic-vue'
    import { isAdmin } from '@/utils/index.js'
    import FastBtn from '@/components/GroupDailys/FastBtn'
    import requestApi from '@/api/request.js'
    const { getGoodDaily, setGoodDaily, evaluateDaily, deleteDaily, updateEvaluateDaily } = requestApi
    export default {
        components: {
            bkButton,
            bkPagination,
            FastBtn,
            bkInput
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
                time: true,
                // 日报评价 弹出框
                isshowDlog: false,
                // 日报评价的内容
                discussContent: '',
                // 之前是否评价过改日报
                isdiscussdaily: false
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
            // 点击评价日报信息
            chooseEvaluate (data) {
                // 当前选中的日报
                this.curSelectDaily = data.id
                // 之前是否评论过这个日报
                this.isdiscussdaily = this.isDiscussDaily(data)
                this.isshowDlog = true
            },
            // 确定评论按钮
            dialogConfirm () {
                // 之前评论过 日报 就是修改
                if (this.isdiscussdaily && this.discussContent.length !== 0) {
                    updateEvaluateDaily(this.curgroupid, this.curSelectDaily, { evaluate_content: this.discussContent }).then(res => {
                        if (res.result) {
                            this.RenderData()
                            this.dialogCancel()
                            this.handleSuccess('评论成功')
                        } else {
                            this.handleSuccess(res.message, 'error')
                        }
                    })
                } else {
                    // 为空之前还评论过 就是删除
                    if (this.discussContent.length === 0 && this.isdiscussdaily) {
                        deleteDaily(this.curgroupid, this.curSelectDaily).then(res => {
                            if (res.result) {
                                this.RenderData()
                                this.dialogCancel()
                                this.handleSuccess('删除成功')
                            } else {
                                this.handleSuccess(res.message, 'error')
                            }
                        })
                    }
                    // 为空 之前还没评论过 提示内容为空
                    if (this.discussContent.length === 0 && !this.isdiscussdaily) {
                        this.handleSuccess('评论内容为空', 'warning')
                    }
                    // 内容不为空之前还没修改过
                    if (this.discussContent.length !== 0 && !this.isdiscussdaily) {
                        evaluateDaily(this.curgroupid, { daily_id: this.curSelectDaily, evaluate: this.discussContent }).then((res) => {
                            if (res.result) {
                                this.RenderData()
                                this.dialogCancel()
                                this.handleSuccess('评论成功')
                            } else {
                                this.handleSuccess(res.message, 'error')
                            }
                        })
                    }
                }
            },
            // 关闭评价日报窗口
            dialogCancel () {
                this.isshowDlog = false
                this.discussContent = ''
            },
            // 判断我之前评论过日报吗
            isDiscussDaily (data) {
                let flat
                for (let i = 0; i < data.evaluate.length; i++) {
                    if (data.evaluate[i].username === this.myMsg.username) {
                        flat = true
                        this.discussContent = data.evaluate[i].evaluate
                    } else {
                        flat = false
                    }
                }
                return flat
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
