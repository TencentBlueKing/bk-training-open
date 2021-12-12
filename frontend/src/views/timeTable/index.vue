<template>

    <div class="body">
        <bk-divider align="left" style="margin-bottom:30px;">
            <div class="container_title">时间安排</div>
        </bk-divider>
        <div class="container">
            <div class="left_container">
                <bk-select :disabled="false" v-model="curGroupId" style="width: 190px;display: inline-block;"
                    ext-cls="select-custom"
                    @selected="handleselect"
                    ext-popover-cls="select-popover-custom"
                    @change="changeGroup(curGroupId)"
                    searchable>
                    <bk-option v-for="group in groupsData"
                        :key="group.id"
                        :id="group.id"
                        :name="group.name">
                    </bk-option>
                </bk-select>
                <bk-button :theme="'primary'" :title="'基础按钮'" style="margin-top:-21px;margin-left:5px;"
                    class="mr10">
                    组名
                </bk-button>
                <bk-select :disabled="false" v-model="curMemberId" style="width: 190px;display: inline-block;"
                    ext-cls="select-custom"
                    ext-popover-cls="select-popover-custom"
                    @change="changeMember(curMemberId)"
                    searchable>
                    <bk-option v-for="member in memberData"
                        :key="member.id"
                        :id="member.id"
                        :name="member.name">
                    </bk-option>
                </bk-select>
                <bk-button :theme="'primary'" :title="'基础按钮'" style="margin-top:-21px;margin-left:5px;"
                    class="mr10">
                    成员
                </bk-button>
                <div style="margin-top:18px;height:707px;">
                    <div v-if="isUser" class="users_list">
                        <div>
                            <bk-button v-for="user in groupUsers" :key="user.id"
                                :theme="user.id === curUserId ? 'primary' : 'default'" style="width:130px;"
                                @click="changeDateOrUser(user.id, '')" class="mr10">
                                {{ user.name }}
                            </bk-button>
                        </div>
                    </div>
                    <div class="date_picker" style="margin-left:0px;">
                        <bk-date-picker class="mr15" style="position:relative;"
                            @change="getGroupFree"
                            v-model="initdategroups"
                            type="daterange"
                            :placeholder="'选择日期'"
                            :ext-popover-cls="'custom-popover-cls'">
                        </bk-date-picker>
                    </div>
                </div>
                <!-- 清除浮动，撑开盒子 -->
                <div style="clear:both;"></div>
            </div>
            <div class="right_container">
                <bk-tab :active.sync="active" type="unborder-card">
                    <bk-tab-panel
                        v-for="(panel) in panels"
                        v-bind="panel"
                        :key="panel.name">
                    </bk-tab-panel>
                </bk-tab>
                <div v-show="active === 'childA'">
                    <bk-table style="margin-top: 15px;"
                        height="555px"
                        :data="freeTimeList"
                        :size="size"
                        :virtual-render="true"
                        @row-mouse-enter="handleRowMouseEnter"
                        @row-mouse-leave="handleRowMouseLeave"
                        @page-change="handlePageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column type="index" label="序列" width="100"></bk-table-column>
                        <bk-table-column label="姓名" prop="username"></bk-table-column>
                        <bk-table-column label="空闲开始时间" prop="start_time"></bk-table-column>
                        <bk-table-column label="空闲结束时间" prop="end_time"></bk-table-column>
                    </bk-table>
                </div>
                <div v-show="active === 'childB'">
                    <div>
                        <bk-button
                            :text="true" title="primary"
                            @click="newApplyDialog.visible = true">
                            +新增空闲时间
                        </bk-button>
                    </div>
                    <bk-dialog
                        @confirm="addFreeTime"
                        theme="primary"
                        v-model="newApplyDialog.visible"
                        title="+新增空闲时间"
                        :header-position="newApplyDialog.headerPosition"
                        :width="newApplyDialog.width"
                        :position="{ top: 20, left: 100 }">
                        <div>
                            <bk-date-picker v-model="initdate"
                                :placeholder="'选择日期时间范围'"
                                :type="'date'"
                                :up-to-now="true"
                                @change="change4UpToNow"
                                @open-change="openChange4UpToNow"
                                @pick-success="pickSuccess4UpToNow"></bk-date-picker>
                            <bk-time-picker v-model="initTimeRange1" :placeholder="'选择时间范围'" :type="'timerange'"></bk-time-picker>

                        </div>
                    </bk-dialog>

                    <bk-dialog
                        @confirm="changeFreeTime"
                        theme="primary"
                        v-model="changeNewApplyDialog.visible"
                        title="修改空闲时间"
                        :header-position="changeNewApplyDialog.headerPosition"
                        :width="changeNewApplyDialog.width"
                        :position="{ top: 20, left: 100 }">
                        <div>
                            <bk-date-picker v-model="initdate"
                                :placeholder="'选择日期时间范围'"
                                :type="'date'"
                                :up-to-now="true"
                                @change="change4UpToNow"
                                @open-change="openChange4UpToNow"
                                @pick-success="pickSuccess4UpToNow"></bk-date-picker>
                            <bk-time-picker v-model="initTimeRange1" :placeholder="'选择时间范围'" :type="'timerange'"></bk-time-picker>
                        </div>
                    </bk-dialog>
                    <bk-table style="margin-top: 15px;"
                        height="555px"
                        :data="myFreeTimeData"
                        :size="size"
                        :virtual-render="true"
                        @row-mouse-enter="handleRowMouseEnter"
                        @row-mouse-leave="handleRowMouseLeave"
                        @page-change="handlePageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column type="index" label="序列" width="100"></bk-table-column>
                        <bk-table-column label="空闲开始时间" prop="start_time"></bk-table-column>
                        <bk-table-column label="空闲结束时间" prop="end_time"></bk-table-column>
                        <bk-table-column label="操作" width="200px">
                            <template slot-scope="props">
                                <bk-button class="mr10" theme="primary" text="true" @click="changeFreeTimebutton(props.row,index)">
                                    修改
                                </bk-button>
                                <bk-button class="mr10" theme="primary" text="true" @click="deleteFreeTime(props.row,index)">移除</bk-button>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </div>
            </div>
            <!-- 清除浮动，撑开盒子 -->
            <div style="clear:both;"></div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { bkTable, bkTableColumn, bkButton, bkDatePicker } from 'bk-magic-vue'
    export default {
        components: {
            bkTable,
            bkTableColumn,
            bkButton,
            bkDatePicker
        },
        data () {
            return {
                // 所有组内成员数据
                // 请假时间
                initTimeRange1: ['00:00:00', '23:59:59'],
                initdategroups: [new Date(), new Date()],
                initdate: new Date(),
                newApplyData: [],
                strdate: '',
                // 所有人空闲时间
                freeTimeData: [],
                // 我的空闲时间
                myFreeTimeData: [],
                newApplyDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                add: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                changeNewApplyDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                size: 'small',
                pagination: {
                    current: 1,
                    count: 500,
                    limit: 20
                },
                panels: [
                    { name: 'childA', label: '空闲时间', count: 10, sign: true },
                    { name: 'childB', label: '我的时间', count: 20, sign: false }
                ],
                // 选择空闲时间还是我的时间
                active: 'childA',
                // 判断用户今天有没有写日报
                myTodayReport: true,
                defaultPaging: {
                    current: 1,
                    limit: 8,
                    count: 0,
                    limitList: [8, 16, 32, 64]
                },
                free_time_id: 0,
                memberData: [],
                memberId: null,
                curMember: {
                    id: '',
                    name: '',
                    create_time: '',
                    update_time: '',
                    username: '',
                    phone: '',
                    email: ''
                },

                formatDate: '',
                // 选择的组
                selectGroupId: 0,
                hasRemindAll: false,
                shareAllList: [],
                shareAllIdList: [],
                hasSharedIdList: [],
                currentUserName: this.$store.state.user.username,
                hasSubmitDaily: [],
                curGroupId: null,
                groupsData: [],
                curMemberId: null,
                membersData: [],
                curUser: {
                    isAdmin: false,
                    info: {
                        id: '',
                        username: ''
                    }
                },
                groupId: '',
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
                    dailys: [],
                    formatTitle: [],
                    formatContent: []
                },
                // 用户列表
                groupUsers: [],
                addUserDialog: {
                    visible: false
                },
                curUserId: null,
                freeTimeList: []
            }
        },
        created () {
            const groupIdInURL = this.$route.query.group
            if (groupIdInURL !== undefined) {
                this.curGroupId = parseInt(groupIdInURL)
            }
            this.init()
        },
        methods: {
            // 新增一条时间
            addFreeTime () {
                this.strdate = this.initdate.getFullYear() + '-' + this.initdate.getMonth() + '-' + this.initdate.getDate() + ' '
                this.$http.post('/free_time/',
                                { 'free_times': [
                                    {
                                        'start_time': this.strdate + this.initTimeRange1[0].slice(0, 5),
                                        'end_time': this.strdate + this.initTimeRange1[1].slice(0, 5)
                                    }
                                ] })
                this.newApplyDialog.visible = false
                this.change.visible = true
                this.init()
            },
            changeFreeTimebutton (id) {
                this.memberId = id.id
                this.changeNewApplyDialog.visible = true
            },
            // 修改空闲时间
            changeFreeTime () {
                this.strdate = this.initdate.getFullYear() + '-' + this.initdate.getMonth() + '-' + this.initdate.getDate() + ' '
                this.$http.patch(/free_time/ + this.memberId + '/',
                                 {
                                     'new_start_date': this.strdate + this.initTimeRange1[0].slice(0, 5),
                                     'new_end_date': this.strdate + this.initTimeRange1[1].slice(0, 5)
                                 },
                                 { 'emulateJSON': true }
                )

                this.init()
            },
            // 删除一条空闲时间
            deleteFreeTime (id) {
                console.log('id', id)
                this.$http.delete(/free_time/ + id.id + '/')
                this.init()
            },
            handlePageLimitChange () {
                console.log('handlePageLimitChange', arguments)
            },
            toggleTableSize () {
                const size = ['small', 'medium', 'large']
                const index = (size.indexOf(this.size) + 1) % 3
                this.size = size[index]
            },
            handlePageChange (page) {
                this.pagination.current = page
            },
            // 请求函数
            // 获取所有蓝鲸用户
            getAllBKUser () {
                this.$http.get('/get_all_bk_users/').then(res => {
                    this.bkUsers = res.data.results
                    console.log('bkUsers', this.bkUsers)
                })
            },
            // 获取组内成员
            getGroupUsers (groupId) {
                this.$http.get('/get_group_users/' + groupId + '/').then(res => {
                    this.memberData = res.data
                    console.log('member:', this.memberData)
                })
            },
            // 获取组员空闲时间信息
            getGroupFree () {
                this.$http.get('/group_free_time/' + this.groupId + '/?start_date=' + moment(this.initdategroups[0]).format('YYYY-MM-DD') + '&end_date=' + moment(this.initdategroups[1]).format('YYYY-MM-DD')
                ).then(res => {
                    console.log('res.data', res.data)
                    this.freeTimeData = res.data
                    for (const freetimes of this.freeTimeData) {
                        for (const freetime of freetimes.free_time) {
                            const obj = {}
                            obj.username = freetimes.username
                            obj.start_time = freetime.start_time
                            obj.end_time = freetime.end_time
                            this.freeTimeList.push(obj)
                        }
                    }
                    console.log('freeTimeList', this.freeTimeList)
                })
                this.getMYFree()
            },
            // 获取本人空闲时间信息
            getMYFree () {
                this.$http.get('/free_time/?start_date=' + moment(this.initdategroups[0]).format('YYYY-MM-DD') + '&end_date=' + moment(this.initdategroups[1]).format('YYYY-MM-DD')
                ).then(res => {
                    this.myFreeTimeData = res.data
                    console.log('myFreeTimeData', this.myFreeTimeData)
                })
            },
         
            // 获取所有组信息
            getAvailableApplyGroups () {
                this.availableGroupsIsLoding = true
                this.$http.get(
                    '/get_available_apply_groups/'
                ).then(res => {
                    this.availableApplyGroups = res.data
                    if (this.availableApplyGroups.length > 0) {
                        this.applyForGroup.groupId = this.availableApplyGroups[0].id
                    }
                }).finally(() => {
                    this.availableGroupsIsLoding = false
                })
            },
            changeGroup (groupId) {
                if (groupId === '' || groupId === null) {
                    console.log('点x')
                    this.curGroupId = null
                    this.curGroup = {
                        id: '',
                        name: '',
                        admin: '',
                        admin_list: [],
                        create_by: '',
                        create_name: '',
                        create_time: ''
                    }
                    this.dailyTemplates = []
                    this.groupUsers = []
                    this.curUser.isAdmin = false
                } else {
                    // 切换组成员信息
                    this.getGroupUsers(groupId)
                    this.getGroupFree(groupId)
                    this.getMYFree()
                }
            },
            init () {
                // 初始化用户信息
                this.$http.get('/get_user/').then((res) => {
                    this.curUser.info = res.data
                    console.log('curUser', this.curUser.info)
                    // 初始化组
                    this.$http.get('/get_user_groups/').then((res) => {
                        // 更新组信息
                        this.groupsData = res.data
                        console.log('init_group, groupsData:', this.groupsData)
                        if (this.groupsData.length !== 0) {
                            this.curGroupId = this.groupsData[0].id
                            this.groupId = this.curGroupId
                            this.getGroupUsers(this.curGroupId)
                            this.changeGroup(this.curGroupId)
                            this.getGroupFree(this.curGroupId)
                        }
                    })
                })
            },
            change4UpToNow (date, type) {
                console.log('change4UpToNow change', date, type)
            },
            openChange4UpToNow (state) {
                console.log('openChange4UpToNow openChange', state)
            },
            pickSuccess4UpToNow () {
                console.log('pickSuccess4UpToNow pickSuccess')
            },
            selected (value) {
      
            }
        } }

</script>
<style scoped>
@import "./index.css";
</style>
