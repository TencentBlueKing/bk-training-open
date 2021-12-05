<template>
    <contentWapper :pageid="pageId" :minheight="pageMinHeight">
        <div class="left_container">
            <div class="select-bar">
                <div class="member-select">
                    <bk-select :disabled="false" v-model="curGroupId"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                        @change="changeGroup(curGroupId)"
                        z-index="99"
                        searchable>
                        <bk-option v-for="group in groupsData"
                            :key="group.id"
                            :id="group.id"
                            :name="group.name">
                        </bk-option>
                    </bk-select>
                    <bk-button :theme="'primary'" type="submit" @click="changeType" style="margin-left:14px;">
                        {{isUser ? '日期' : '成员'}}
                    </bk-button>
                </div>
                <div class="date-select">
                    <div v-if="isUser" class="users_list">
                        <div class="users_list_title">
                            请选择成员：
                        </div>
                        <bk-button v-show="user.username !== 'admin'" v-for="user in groupUsers" :key="user.id" :theme="user.id === curUserId ? 'primary' : 'default'" @click="clickUser(user.id)" class="mr10">
                            {{user.username}}({{user.name}})
                        </bk-button>
                    </div>
                    <div class="date_picker" v-else>
                        <bk-date-picker class="mr15" @change="changeDate(curDate)" style="position:relative;" v-model="curDate"
                            placement="bottom-end"
                            :placeholder="'选择日期'"
                            @open-change="datePickerOpenChange"
                            :open="isDatePickerOpen"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption">
                        </bk-date-picker>
                    </div>
                </div>
            </div>
                
        </div>
        <div class="right_container">
            <!-- 显示筛选日报个数等 -->
            <div v-show="rightIsUser" class="report-info">
                <div class="report-num-select">
                    <span>显示日报个数：</span>
                    <bk-select :disabled="false" v-model="curDailyNum"
                        style="display:inline-block; width:80px;"
                        ext-cls="select-custom"
                        ext-popover-cls="select-popover-custom"
                        @change="changeDailyNum()"
                    >
                        <bk-option v-for="num in numlist"
                            :key="num.value"
                            :id="num.value"
                            :name="num.name">
                        </bk-option>
                    </bk-select>
                </div>
                <span>日报总数：{{dailysData.count}}</span>
            </div>
            <div v-if="dailysData.dailys.length === 0" class="no-report">
                没有日报内容哟~
            </div>
            <div>
                <bk-card v-for="daily in dailysData.dailys" :key="daily.id" :title="daily.create_by + '(' + (daily.create_name) + ')' + '-' + '日报'" class="card" style="float:left;margin-bottom:10px;">
                    <div>日期：{{daily.date}}</div>
                    <div>日报状态：{{daily.send_describe}}</div>
                    <div v-for="(value, key) in daily.content" :key="key">
                        <p style="font-weight: 700;font-size:18px;">{{key}}</p>
                        <p>{{value}}</p>
                    </div>
                </bk-card>
            </div>
        </div>

        <!-- 清除浮动，撑开盒子 -->
        <div style="clear:both;"></div>
    </contentWapper>

</template>

<script>
    import contentWapper from '../components/content-wapper.vue'
    export default {
        components: {
            contentWapper
        },
        data () {
            return {
                pageId: 'groupDailys',
                pageMinHeight: 830,
                isDatePickerOpen: false,
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
                rightIsUser: false,
                // 日期选择（当前正常，get时需要再次转化）
                curDate: new Date(),
                // 日报数据
                dailysData: {
                    count: 100,
                    dailys: []
                },
                // 用户列表
                groupUsers: [],
                curUserId: null,
                curDailyNum: 7,
                numlist: [{ 'name': 7, 'value': 7 }, { 'name': 14, 'value': 14 }, { 'name': 30, 'value': 30 }, { 'name': '全部', 'value': 0 }]
            }
        },
        created () {
            this.init()
        },
        methods: {
            // 点击切换显示类型的按钮
            changeType () {
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
                    console.log('curGroup-userlist', this.groupUsers)
                })
            },
            // 根据成员获取对应日报
            getUserDailys (userId) {
                // 获取日报
                this.$http.get('/report_filter/' + this.curGroupId + '/?' + 'member_id=' + userId + '&report_num=' + this.curDailyNum).then((res) => {
                    if (res.result) {
                        // 更新daily
                        console.log('dailys', res.data)
                        this.dailysData.count = res.data.total_report_num
                        this.dailysData.dailys = res.data.reports
                    } else {
                        const config = {}
                        config.message = res.message
                        config.offsetY = 80
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            clickUser (userId) {
                this.curUserId = userId
                this.rightIsUser = true
                this.getUserDailys(userId)
            },
            // 切换获取日报数量
            changeDailyNum () {
                if (this.curDailyNum === '全部') {
                    this.curDailyNum = 0
                }
                this.getUserDailys(this.curUserId)
            },
            init () {
                const str = "{'感想':'测试1','内容':'测试内容'}"
                const json1 = JSON.parse(str.replace(/'/g, '"'))
                console.log('json', json1)
                // console.log('beforeToday', new Date((new Date()).getTime() - 24 * 60 * 60 * 1000))
                // 获取所有组列表
                this.$http.get('/get_user_groups/').then((res) => {
                    // 更新组信息
                    this.groupsData = res.data
                    console.log('init_group, groups:', this.groupsData)
                    // 初始化组，选择第一个
                    if (this.groupsData.length !== 0) {
                        this.curGroupId = this.groupsData[0].id
                        this.curGroup = this.groupsData[0]
                        console.log('curGroup', this.curGroup)
                        // 获取组内成员
                        this.getGroupUsers(this.curGroupId)
                        // 初始化组内所有日报（根据日期选择）
                        this.changeDate(this.curDate)
                    }
                })
            },
            // 点击切换组
            changeGroup (groupId) {
                if (groupId === null || groupId === '') {
                    console.log('x')
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
                    this.rightIsUser = false
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
                    this.curDate = new Date()
                    this.changeDate(this.curDate)
                }
            },
            datePickerOpenChange (state) {
                this.isDatePickerOpen = state
            },
            // 根据日期获取当前组日报
            changeDate (date) {
                this.curUserId = null
                this.rightIsUser = false
                if (this.curGroupId === null || this.curGroupId === '') {
                    console.log('curGroupId为空')
                } else {
                    console.log('curDate：', date)
                    console.log('month', date.getMonth())
                    const paramDate = date.getFullYear() + '-' + (date.getMonth() >= 9 ? (date.getMonth() + 1) : '0' + (date.getMonth() + 1)) + '-' + (date.getDate() > 9 ? (date.getDate()) : '0' + (date.getDate()))
                    console.log('paramDate', paramDate)
                    this.$http.get('/report_filter/' + this.curGroupId + '/?date=' + paramDate).then(res => {
                        // this.rightIsUser = false
                        if (res.result) {
                            console.log('groupDailys', res.data)
                            this.dailysData.count = res.data.length
                            this.dailysData.dailys = res.data
                        } else {
                            const config = {}
                            config.message = res.message
                            config.offsetY = 80
                            config.theme = 'error'
                            this.$bkMessage(config)
                        }
                    })
                }
            }
        }
    }
</script>

<style scoped>
@import "./index.css";
    #groupDailys /deep/ .content{
        display: flex;
        min-width: 1000px;
    }
    .container_title {
        font-size: 22px;
        font-weight: 700;
    }
    .left_container{
        width: 360px;
        min-width: 358px;
        border-right: 1px solid #EAEBF0 ;
        padding-right: 10px;
    }
    .select-bar{
        width: 100%;
        display: flex;
        flex-wrap: wrap;
    }
    .member-select{
        display: flex;
        margin-right: 10px;
    }
    .member-select /deep/ .bk-select{
        min-width: 110px;
    }
    .users_list{
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
    }
    .users_list .users_list_title{
        font-size: 16px;
        width: 100%;
        height: 32px;
        line-height: 32px;
    }
    .users_list /deep/ .bk-button{
        margin-bottom: 10px;
        
    }
    .right_container{
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
    .card /deep/ .bk-card-body{
        height: 280px;
        overflow-y: auto;
        padding-top: 10px;
    }
    .date_picker /deep/ .bk-date-picker-dropdown{
        top: 32px !important;
    }
    .date_picker /deep/ .bk-date-picker{
        width: 124px;
    }
</style>
