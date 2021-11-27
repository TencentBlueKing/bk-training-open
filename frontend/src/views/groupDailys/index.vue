<template>
    <div class="body">
        <bk-divider align="left" style="margin-bottom:30px;">
            <div class="container_title">日报查看</div>
        </bk-divider>
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
                            <bk-button v-for="user in groupUsers" :key="user.id" :theme="user.id === curUserId ? 'primary' : 'default'" style="width:130px;" @click="clickUser(user.id)" class="mr10">
                                {{user.name}}
                            </bk-button>
                        </div>
                    </div>
                    <div class="date_picker" style="margin-left:0px;" v-else>
                        <bk-date-picker class="mr15" @change="changeDate(curDate)" style="position:relative;" v-model="curDate"
                            :placeholder="'选择日期'"
                            open="true"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption">
                        </bk-date-picker>
                    </div>
                </div>
            </div>
            <div class="right_container">
                <div v-if="dailysData.dailys.length === 0" style="margin: 200px auto;width:140px;">
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

                <!-- 清除浮动，撑开盒子 -->
                <div style="clear:both;"></div>

                <bk-pagination
                    @change="changePage"
                    @limit-change="changeLimit"
                    :current.sync="defaultPaging.current"
                    :count.sync="defaultPaging.count"
                    :limit="defaultPaging.limit"
                    :limit-list="defaultPaging.limitList">
                </bk-pagination>
            </div>

            <!-- 清除浮动，撑开盒子 -->
            <div style="clear:both;"></div>
        </div>
    </div>
</template>

<script>
    import { bkPagination } from 'bk-magic-vue'

    export default {
        components: {
            bkPagination
        },
        data () {
            return {
                defaultPaging: {
                    current: 1,
                    limit: 8,
                    count: 0,
                    limitList: [8, 16, 32]
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
                rightIsUser: false,
                // 日期选择（当前正常，get时需要再次转化）,在点击成员时将其设为空字符串来判断当前分页调用哪个接口
                curDate: new Date(),
                // 日报数据
                dailysData: {
                    dailys: []
                },
                // 用户列表
                groupUsers: [],
                curUserId: null
            }
        },
        created () {
            this.init()
        },
        methods: {
            
            // 每页日报数量
            changeLimit (pageSize) {
                this.defaultPaging.limit = pageSize
                if (this.curDate === '') {
                    this.getUserDailys(this.curUserId)
                } else {
                    this.changeDate(this.curDate)
                }
            },
            // 切换页面
            changePage (page) {
                this.defaultPaging.current = page
                if (this.curDate === '') {
                    this.getUserDailys(this.curUserId)
                } else {
                    this.changeDate(this.curDate)
                }
            },
            // 点击切换显示类型的按钮
            changeType () {
                this.isUser = !this.isUser
                if (!this.isUser) {
                    this.changeGroup(this.curGroupId)
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
                if (userId == null) {
                    userId = this.curUserId
                }
                this.$http.get('/report_filter/' + this.curGroupId + '/?' + 'member_id=' + userId + '&size=' + this.defaultPaging.limit + '&page=' + this.defaultPaging.current).then((res) => {
                    if (res.result) {
                        // 更新daily
                        console.log('dailys', res.data)
                        this.defaultPaging.count = res.data.total_report_num
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
                this.curDate = ''
                this.curUserId = userId
                this.rightIsUser = true
                this.getUserDailys(userId)
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
                    this.$http.get('/report_filter/' + this.curGroupId + '/?date=' + paramDate + '&page=' + this.defaultPaging.current).then(res => {
                        // this.rightIsUser = false
                        if (res.result) {
                            console.log('groupDailys', res.data)
                            this.defaultPaging.count = res.data.length
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
    .body{
        border: 2px solid #EAEBF0 ;
        /* border-radius: 4px; */
        margin:0px 100px;
        padding: 20px 50px;
        
    }
    .container_title {
        font-size: 22px;
        font-weight: 700;
    }
    .left_container{
        float: left;
        width: 360px;
        padding-left: 20px;
        border-right: 1px solid #EAEBF0 ;
    }
    .users_list >>> .bk-button{
        margin-bottom: 10px;
        
    }
    .right_container{
        float: right;
        min-width: 380px;
        width: calc(100% - 380px);
    }
    .card{
        float: left;
        width: calc(46% - 5px);
        margin-right: 18px;
    }
    .card >>> .bk-card-body{
        height: 280px;
        overflow-y: auto;
        padding-top: 10px;
    }
    .date_picker >>>.bk-date-picker-dropdown{
        top: 32px !important;
    }
</style>
