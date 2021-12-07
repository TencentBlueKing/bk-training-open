<template>
    <div class="body">
        <div class="container">
            <div class="left_container">
                <bk-select :disabled="false" v-model="curGroupId" style="width: 190px;display: inline-block;"
                    ext-cls="select-custom"
                    ext-popover-cls="select-popover-custom"
                    @change="changeGroup(curGroupId)"
                    searchable>
                    <bk-option v-for="group in groupsData"
                        :key="group.id"
                        :id="group.id"
                        :name="group.name">
                    </bk-option>
                </bk-select>
                <bk-button :theme="'primary'" type="submit" :title="'基础按钮'" style="margin-top:-21px;margin-left:5px;" @click="changeType" class="mr10">
                    {{isUser ? '日期' : '成员'}}
                </bk-button>
                <div style="margin-top:18px;height:707px;">
                    <div v-if="isUser" class="users_list">
                        <div>
                            <bk-button v-for="user in groupUsers" :key="user.id" :theme="user.id === curUserId ? 'primary' : 'default'" style="width:130px;" @click="changeDateOrUser(user.id, '')" class="mr10">
                                {{user.name}}
                            </bk-button>
                        </div>
                    </div>
                    <div class="date_picker" style="margin-left:0px;" v-else>
                        <bk-date-picker class="mr15" @change="changeDateOrUser('', changeDate)" style="position:relative;" v-model="changeDate" format="yyyy-MM-dd"
                            :placeholder="'选择日期'"
                            :open="true"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption">
                        </bk-date-picker>
                    </div>
                </div>

                <!-- 清除浮动，撑开盒子 -->
                <div style="clear:both;"></div>
            </div>
            <div class="right_container">
                <div v-if="!myTodayReport" style="margin-bottom: 10px;">
                    <bk-alert type="warning" title="警告的提示文字">
                        <bk-link theme="warning" slot="title" :href="link">您当天未提交日报，可点击链接前往补签</bk-link>
                    </bk-alert>
                </div>
                <div class="report-tabs">
                    <div :class="{
                        'header-tabs': true,
                        'tabs-active': title === activeTabTitle
                    }" v-for="(title,tindex) in tabTitleList" :key="tindex" @click="activeTabTitle = title">
                        {{title}}
                    </div>
                </div>
                <div class="all-report-wapper report-wapper" v-if="activeTabTitle === tabTitleList[0]">
                    <div v-if="defaultPaging.count === 0" class="all-empty">
                        没有日报内容哟~
                    </div>
                    <div class="all-report-body">
                        <bk-card class="all-report-card card"
                            v-for="(daily, index) in dailysData.dailys"
                            :key="index"
                            :title="daily.create_by + '(' + (daily.create_name) + ')' + '-' + '日报'">
                            <div>日期：{{daily.date}}</div>
                            <div>日报状态：{{daily.send_describe}}</div>
                            <div v-for="(dailyContnet, innerIndex) in daily.content" :key="innerIndex">
                                <h2>{{dailyContnet.title}}</h2>
                                <div v-if="dailyContnet.type === 'table'" style="font-size: 18px">
                                    <div v-for="(row, iiIndex) in dailyContnet.content" :key="iiIndex">
                                        <pre>({{iiIndex + 1}}){{row.text}}</pre><span v-if="curUserName === daily.create_by || !row.isPrivate">----({{row.cost}})</span>
                                    </div>
                                </div>
                                <div v-else>
                                    {{dailyContnet.text}}
                                </div>
                            </div>
                        </bk-card>
                    </div>
                    <bk-pagination
                        @change="changePage"
                        @limit-change="changeLimit"
                        ext-cls="bottom-paging"
                        show-total-count="true"
                        :current.sync="defaultPaging.current"
                        :count.sync="defaultPaging.count"
                        :limit="defaultPaging.limit"
                        :limit-list="defaultPaging.limitList">
                    </bk-pagination>
                </div>
                <div class="perfect-report-wapper report-wapper" v-else>
                    <div class="right-top-bar">
                        <div class="select-bar">
                            <bk-select :disabled="false" v-model="perfectShowType" style="width: 150px;"
                                ext-cls="select-type"
                                behavior="simplicity"
                                placeholder="请选择查看类型"
                                ext-popover-cls="select-popover-custom"
                                @change="changeShowType"
                                placement="bottom-end">
                                <bk-option v-for="option in pecfectTypeList"
                                    :key="option.id"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                        <bk-date-picker
                            :disabled="perfectSetting.perfectShowType === 1"
                            behavior="simplicity"
                            :type="perfectSetting.DateSelectType"
                            :format="perfectSetting.DateType"
                            ext-cls="perfect-date-picker"
                            v-model="perfectDate"
                            @change="perfectDateChange"
                            :placeholder="'选择日期'">
                        </bk-date-picker>
                    </div>
                    <div class="perfect-body">
                        <div v-if="perfectPaging.count === 0" class="perfect-empty">
                            没有日报内容哟~
                        </div>
                        <div class="perfect-cards">
                            <bk-card class="perfect-report-card card"
                                v-for="(pdaily, pindex) in perfectDailysData.daily_list"
                                :key="pindex"
                                :title="pdaily.create_by + '(' + (pdaily.create_name) + ')' + '-' + '日报'">
                                <div>日期：{{pdaily.date}}</div>
                                <div>日报状态：{{pdaily.send_describe}}</div>
                                <div v-for="(perfectContnet, innerIndex) in pdaily.content" :key="innerIndex">
                                    <h2>{{perfectContnet.title}}</h2>
                                    <div v-if="perfectContnet.type === 'table'" style="font-size: 18px">
                                        <div v-for="(row, iiIndex) in perfectContnet.content" :key="iiIndex">
                                            <pre>({{iiIndex + 1}}){{row.text}}</pre><span v-if="curUserName === pdaily.create_by || !row.isPrivate">----({{row.cost}})</span>
                                        </div>
                                    </div>
                                    <div v-else>
                                        {{perfectContnet.text}}
                                    </div>
                                </div>
                            </bk-card>
                        </div>
                    </div>
                    <bk-pagination
                        @change="changePerfectPage"
                        @limit-change="changePerfectLimit"
                        ext-cls="bottom-paging"
                        show-total-count="true"
                        :current.sync="perfectPaging.current"
                        :count.sync="perfectPaging.count"
                        :limit="perfectPaging.limit"
                        :limit-list="perfectPaging.limitList">
                    </bk-pagination>
                </div>
                <!-- 清除浮动，撑开盒子 -->
                <div style="clear:both;"></div>
            </div>
            <!-- 清除浮动，撑开盒子 -->
            <div style="clear:both;"></div>
        </div>
    </div>
</template>

<script>
    import { bkPagination, bkSelect, bkOption, bkDatePicker } from 'bk-magic-vue'
    import moment from 'moment'

    export default {
        components: {
            bkPagination, bkSelect, bkOption, bkDatePicker
        },
        data () {
            return {
                // 判断用户今天有没有写日报
                myTodayReport: true,
                defaultPaging: {
                    current: 1,
                    limit: 8,
                    count: 0,
                    limitList: [8, 16, 32, 64]
                },
                groupsData: [],
                curGroupId: null,
                curGroup: {
                    id: '',
                    name: '',
                    admin: [],
                    create_by: '',
                    create_name: '',
                    create_time: ''
                },
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                // 控制显示日期还是显示成员
                isUser: false,
                // 日期选择（当前正常，get时需要再次转化）,在点击成员时将其设为空字符串来判断当前分页调用哪个接口
                curDate: moment(new Date()).format('YYYY-MM-DD'),
                // 日报数据
                dailysData: {
                    count: 100,
                    dailys: []
                },
                // 用户列表
                groupUsers: [],
                curUserId: null,
                curUserName: this.$store.state.user.username,
                tabTitleList: [
                    '所有日报',
                    '优秀日报'
                ],
                activeTabTitle: '所有日报',
                pecfectTypeList: [
                    { id: 1, name: '全部' },
                    { id: 2, name: '按月' }
                ],
                perfectDate: new Date(),
                perfectSetting: {
                    perfectShowType: 1,
                    DateType: 'yyyy-MM',
                    DateSelectType: 'month'
                },
                perfectPaging: {
                    current: 1,
                    limit: 8,
                    count: 0,
                    limitList: [8, 16, 32, 64]
                },
                perfectDailysData: {
                    daily_list: []
                }
            }
        },
        computed: {
            link () {
                return window.PROJECT_CONFIG.SITE_URL + '/home/?date=' + this.curDate
            }
        },
        created () {
            // 初始化组id和日期
            const groupIdInURL = this.$route.query.group
            if (groupIdInURL !== undefined) {
                this.curGroupId = parseInt(groupIdInURL)
            }
            this.init()
        },
        methods: {
            // 每页日报数量
            changeLimit (pageSize) {
                this.defaultPaging.limit = pageSize
                if (this.curUserId === '' && this.curDate === '') {
                    this.curDate = moment(new Date()).format('YYYY-MM-DD')
                }
                this.getDailys()
            },
            // 切换页面
            changePage (page) {
                this.defaultPaging.current = page
                if (this.curUserId === '' && this.curDate === '') {
                    this.curDate = moment(new Date()).format('YYYY-MM-DD')
                }
                this.getDailys()
            },
            // 点击切换显示类型的按钮
            changeType () {
                this.myTodayReport = true
                this.isUser = !this.isUser
                if (!this.isUser) {
                    this.changeGroup(this.curGroupId)
                    document.querySelector('.left_container').style.minWidth = 290
                    console.log('left_container == ', document.querySelector('.left_container').style.minWidth)
                } else {
                    document.querySelector('.left_container').style.minWidth = 350
                }
            },
            // 获取组内成员
            getGroupUsers (groupId) {
                // 根据组id获取组成员
                this.$http.get('/get_group_users/' + groupId + '/').then((res) => {
                    this.groupUsers = res.data
                })
            },
            // 修改日期或成员
            changeDateOrUser (userId, date) {
                this.curDate = date === '' ? '' : moment(date).format('YYYY-MM-DD')
                this.curUserId = userId
                if (this.curUserId === '' && this.curDate === '') {
                    this.curDate = moment(new Date()).format('YYYY-MM-DD')
                }
                this.getDailys()
            },
            // 获取当前组日报
            getDailys () {
                this.$http.get('/report_filter/' + this.curGroupId + '/?date=' + this.curDate + '&member_id=' + this.curUserId + '&size=' + this.defaultPaging.limit + '&page=' + this.defaultPaging.current).then(res => {
                    if (res.result) {
                        this.defaultPaging.count = res.data.total_report_num
                        this.dailysData.dailys = res.data.reports
                        if (res.data.my_today_report !== undefined) {
                            this.myTodayReport = res.data.my_today_report
                        } else {
                            // 响应无my_today_report参数为查看成员全部日报，不提示补签
                            this.myTodayReport = true
                        }
                        if (this.isUser) {
                            // 查看某组员全部日报，不提示补签
                            this.myTodayReport = true
                        }
                    } else {
                        const config = {
                            message: res.message,
                            offsetY: 80,
                            theme: 'error'
                        }
                        this.$bkMessage(config)
                    }
                })
            },
            init () {
                // 获取所有组列表
                this.$http.get('/get_user_groups/').then((res) => {
                    // 更新组信息
                    this.groupsData = res.data
                    // 初始化显示的组
                    if (this.groupsData.length !== 0 && this.groupsData.length !== undefined) {
                        if (this.curGroupId !== null) {
                            const vm = this
                            this.groupsData.forEach(function (group) {
                                if (group.id === vm.curGroupId) {
                                    vm.curGroup = group
                                    // 获取组内成员
                                    vm.getGroupUsers(vm.curGroupId)
                                    // 初始化组内所有日报（根据日期选择）
                                    vm.changeDateOrUser('', vm.curDate)
                                }
                            })
                        } else {
                            this.curGroupId = this.groupsData[0].id
                            this.curGroup = this.groupsData[0]
                        }
                        // 获取优秀日报
                        this.getPerfectReport()
                    }
                    // 获取优秀日报
                    this.getPerfectReport()
                })
            },
            // 点击切换组
            changeGroup (groupId) {
                if (groupId === null || groupId === '') {
                    this.curGroup = {
                        id: '',
                        name: '',
                        admin: [],
                        create_by: '',
                        create_name: '',
                        create_time: ''
                    }
                    this.groupUsers = []
                    this.curUserId = null
                    this.dailysData.dailys = []
                } else {
                    const vm = this
                    // 更改当前组信息
                    this.groupsData.forEach(function (group) {
                        if (group.id === groupId) {
                            vm.curGroup = group
                        }
                    })
                    // 更改组用户
                    this.getGroupUsers(groupId)
                    // 更改界面为日期显示
                    this.isUser = false
                    // 初始化组内所有日报（根据日期选择）,设置日期为今天的前一天
                    this.changeDateOrUser('', new Date())
                    // 获取该组所有优秀日报
                    this.getPerfectReport()
                }
            },
            // 优秀日报展示模型切换
            changeShowType (newValue, oldValue) {
                this.perfectSetting.perfectShowType = newValue
                if (this.pecfectTypeList[newValue - 1].name === '按月') {
                    this.perfectSetting.DateType = 'yyyy-MM'
                    this.perfectSetting.DateSelectType = 'month'
                } else if (this.pecfectTypeList[newValue - 1].name === '全部') {
                    this.getPerfectReport()
                }
            },
            // 获取优秀日报
            getPerfectReport () {
                const selectType = this.perfectSetting.perfectShowType === 1 ? 'all' : 'month'
                this.$http.get('/get_prefect_dailys/' + this.curGroupId
                    + '/?select_type=' + selectType
                    + '&page=' + this.perfectPaging.current
                    + '&size=' + this.perfectPaging.limit
                    + '&year=' + moment(this.perfectDate).format('YYYY')
                    + '&month=' + moment(this.perfectDate).format('MM')
                ).then((res) => {
                    if (res.result) {
                        this.perfectDailysData = res.data
                        this.perfectPaging.count = res.data.total_num
                    } else {
                        this.$bkMessage({
                            'offsetY': 80,
                            'delay': 2000,
                            'theme': 'warning',
                            'message': res.message
                        })
                    }
                })
            },
            // 优秀日报年份切换
            perfectDateChange (date, type) {
                this.getPerfectReport()
            },
            // 优秀日报每页日报数量
            changePerfectLimit (pageSize) {
                this.perfectPaging.limit = pageSize
                this.getPerfectReport()
            },
            // 优秀日报切换页面
            changePerfectPage (page) {
                this.perfectPaging.current = page
                this.getPerfectReport()
            }
        }
    }
</script>

<style scoped>
@import "./index.css";
    .body{
        border: 2px solid #EAEBF0 ;
        margin:0 100px;
        padding: 20px 30px;
    }
    .container_title {
        font-size: 22px;
        font-weight: 700;
    }
    .left_container{
        float: left;
        width: 306px;
        padding-left: 20px;
        border-right: 1px solid #EAEBF0 ;
    }
    .users_list >>> .bk-button{
        margin-bottom: 10px;
    }
    .right_container{
        float: right;
        min-width: 380px;
        width: 100%;
        padding-left: 20px;
    }
    .no-report{
        width: 100%;
        height: 600px;
        line-height: 600px;
        text-align: center;
    }
    .right_container .report-info{
        height: 40px;
        line-height: 40px;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }
    .report-num-select{
        display: flex;
        flex-wrap: nowrap;
        align-items: center;
    }
    .report-num-select span{
        width: 112px;
        margin-bottom: 10px;
    }
    .card{
        float: left;
        width: calc(46% - 5px);
        margin-right: 18px;
    }
    .card >>> .bk-card-body{
        height: 260px;
        overflow-y: auto;
        padding-top: 10px;
    }
    .date_picker >>>.bk-date-picker-dropdown{
        top: 32px !important;
    }
    .demo-block.demo-alert .bk-alert{
        margin-bottom: 20px;
    }

    .right_container .report-tabs{
        display: flex;
        width: 100%;
    }
    .right_container .report-tabs .header-tabs{
        width: 50%;
        height: 30px;
        text-align:center;
        border-bottom: 1px solid rgb(196, 198, 204);
    }
    .right_container .report-tabs .tabs-active{
        border-bottom: 2px solid #3a84ff;
        color: #3a84ff;
    }
    .right_container .report-tabs .header-tabs:hover{
        cursor: pointer;
        color: #3a84ff;
    }
    .right_container .report-wapper .bottom-paging{
        display: flex;
        justify-content: flex-end;
        width: 100%;
        align-items: center;
        height: 50px;
    }
    .right_container .perfect-report-wapper .perfect-body{
        width: 100%;
        height: 630px;
    }
    .right_container .perfect-report-wapper .perfect-body .perfect-empty{
        line-height: 600px;
        text-align: center;
    }
    .right_container .perfect-report-wapper .perfect-cards .perfect-report-card{
        width: 200px !important;
    }
    .right_container .perfect-report-wapper .perfect-cards .perfect-report-card /deep/ .bk-card-head{
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        font-size: 16px;
        width: 100% !important;
    }
    .right_container .report-wapper{
        display: flex;
        width: 100%;
        flex-wrap: wrap;
    }
    .right_container .all-report-wapper{
        padding-top: 14px;
    }
    .right_container .all-report-wapper .all-empty{
        width: 100%;
        height: 600px;
        line-height: 600px;
        text-align: center;
        padding-top: 10px;
    }
    .right_container .all-report-wapper .all-report-body{
        height: 650px;
    }
    .right_container .all-report-wapper .all-report-body .all-report-card{
        float: left;
        margin-bottom: 10px;
        width: 200px;
    }
    .right_container .all-report-wapper .all-report-body .all-report-card /deep/ .bk-card-head{
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        font-size: 16px;
        width: 100% !important;
    }
    .right_container .perfect-report-wapper .right-top-bar{
        display: flex;
        justify-content: space-between;
        width: 100%;
        align-items: center;
        height: 50px;
    }
    .right_container .perfect-report-wapper .perfect-date-picker{
        width: 112px !important;
    }
    .right_container .report-wapper .select-bar{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
    }
    .right_container .report-wapper .select-bar .select-type{
        width: 120px !important;
    }
    .right_container .report-wapper .right-bottom-bar{
        display: flex;
        justify-content: space-between;
        width: 100%;
        align-items: center;
        height: 50px;
    }
</style>
