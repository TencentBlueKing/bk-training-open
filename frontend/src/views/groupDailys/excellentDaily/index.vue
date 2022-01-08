<template>
    <div class="excellentdaily">
        <div class="excellentdaily-btn">
            <TabBtn :content="tabBtnContent" @changeType="changeType" />
            <div class="excellentdaily-date-select" v-show="selectType === 2">
                <bk-date-picker type="month" @change="changeDate" style="width: 250px;" :clearable="false" behavior="simplicity" class="mr15" v-model="curDateTime"></bk-date-picker>
            </div>
        </div>
        <!-- 渲染的内容 -->
        <div class="excellentdaily-renderlistbox" v-show="renderDaily && renderDaily.length">
            <bk-card class="all-report-card card"
                v-for="(daily, index) in renderDaily"
                :key="index"
                :title="daily.create_by + '(' + (daily.create_name) + ')'">
                <div class="card-header" slot="header" :title="daily.create_by + '(' + (daily.create_name) + ')'">
                    {{daily.create_by + '(' + (daily.create_name) + ')'}}
                </div>
                <div class="excellentdaily-card-time">{{daily.date}}</div>
                <div v-for="(dailyContnet, innerIndex) in daily.content" :key="innerIndex">
                    <h5 class="sub-title">{{dailyContnet.title}}</h5>
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
                <bk-exception :options="customOption" ext-cls="notrender-box" class="exception-wrap-item exception-part" type="empty" scene="part" :class="{ 'exception-gray': isGray }"> 现在还没有优秀日报 </bk-exception>
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { bkPagination } from 'bk-magic-vue'
    import TabBtn from '@/components/TabBtn/index.vue'
    import requestApi from '@/api/request.js'
    const { getGoodDaily } = requestApi
    export default {
        components: {
            TabBtn,
            bkPagination
        },
        data () {
            return {
                tabBtnContent: ['全部', '日期'],
                myMsg: JSON.parse(window.localStorage.getItem('userMsg')),
                curGroupID: '',
                // 当前选中的类型 1 是 all , 2 是month
                selectType: 1,
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
                }
            }
        },
        computed: {
            curGroupIDChange () {
                return this.$store.state.groupDaily.curGroupID
            }
        },
        watch: {
            curGroupIDChange (oldVal) {
                this.curGroupID = oldVal
                // 组变化 初始化数据
                this.RenderData(oldVal)
            }
        },
        created () {
            this.initData()
        },
        methods: {
            // 初始化调用
            initData () {
                this.curGroupID = this.$route.params.groupId
                this.RenderData(this.$route.params.groupId)
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
                this.RenderData(this.curGroupID)
            },
            // 日期改变
            changeDate (date) {
                this.pagingDevice.curPage = 1
                this.curDateTime = date
                this.RenderData(this.curGroupID)
            },
            // 切换页码
            changePage (curPage) {
                this.pagingDevice.curPage = curPage
                this.RenderData(this.curGroupID)
            },
            // 分页尺寸的变化
            changeLimit (curlimit) {
                this.pagingDevice.curPage = 1
                this.pagingDevice.limit = curlimit
                this.RenderData(this.curGroupID)
            },
            // 渲染数据的设置
            RenderData (curGroupID, year = '', month = '') {
                const { curPage, limit } = this.pagingDevice
                let type
                // 按什么类型搜索
                if (this.selectType === 1) {
                    type = 'all'
                } else {
                    type = 'month'
                    year = moment(this.curDateTime).format('YYYY')
                    month = moment(this.curDateTime).format('MM')
                }
                getGoodDaily(curGroupID, type, curPage, limit, year, month).then(res => {
                    this.pagingDevice.count = res.data.total_report_num
                    this.renderDaily = res.data.daily_list
                })
            }
        }
    }
</script>

<style src='./index.css' scoped ></style>
