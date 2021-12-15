<template>
    <div id="myGroup">
        <div class="body">
            <div class="line-container group-info" style="margin-top:30px;">
                <bk-divider align="left">
                    <div class="container-label">基本信息</div>
                </bk-divider>
                <span style="float:left; margin-top:12px; margin-left:21px;">组名：</span>
                <bk-select :disabled="false" v-model="curGroupId" style="width: 250px; margin-top:10px; display: inline-block;"
                    ext-cls="select-custom"
                    ext-popover-cls="select-popover-custom"
                    searchable
                    @change="changeGroup(curGroupId)">
                    <bk-option v-for="option in groupsData"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                    </bk-option>
                </bk-select>
                <bk-button :theme="'primary'" style="margin-left:30px; margin-top:-20px;" class="mr10" @click="addGroupDialog.visible = true">
                    +新增组
                </bk-button>
                <bk-dialog v-model="addGroupDialog.visible" theme="primary" title="新增组" class="add-group-dialog" :show-footer="false">
                    <bk-form label-width="120">
                        <bk-form-item label="组名称" required="true">
                            <bk-input v-model="addGroupData.formData.name"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="管理员" required="true">
                            <bk-select style="width: 250px; margin-top: 10px;"
                                searchable
                                multiple
                                display-tag
                                v-model="addGroupData.adminIds">
                                <bk-option v-for="option in bkUsers"
                                    :key="option.id"
                                    :id="option.id"
                                    :name="option.username + '(' + option.display_name + ')'">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button style="margin-left: 20px;margin-right: 40px;" theme="primary" title="提交" @click.stop.prevent="addGroup">提交</bk-button>
                            <bk-button ext-cls="mr5" @click="addGroupDialog.visible = false" theme="default" title="取消">取消</bk-button>
                        </bk-form-item>
                    </bk-form>
                </bk-dialog>
                <bk-button v-show="curUser.isAdmin" :disabled="!curUser.isAdmin" :theme="'primary'" :title="'主要按钮'" class="mr10" ref="adminClick" style="margin-top:-20px;" @click="clickEditGroup">
                    编辑组
                </bk-button>
                <bk-dialog v-model="editGroupDialog.visible" theme="primary" title="修改组信息" class="add-group-dialog" :show-footer="false">
                    <bk-form label-width="120">
                        <bk-form-item label="组名称" required="true">
                            <bk-input v-model="editGroupData.formData.name"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="管理员" required="true">
                            <bk-select style="width: 250px; margin-top: 10px;"
                                searchable
                                multiple
                                display-tag
                                v-model="editGroupData.adminIds">
                                <bk-option v-for="option in bkUsers"
                                    :key="option.id"
                                    :id="option.id"
                                    :name="option.username + '(' + option.display_name + ')'">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button style="margin-left: 20px;margin-right: 40px;" theme="primary" title="提交" @click.stop.prevent="editGroup(curGroupId)">提交</bk-button>
                            <bk-button ext-cls="mr5" @click="editGroupDialog.visible = false" theme="default" title="取消">取消</bk-button>
                        </bk-form-item>
                    </bk-form>
                </bk-dialog>
                <bk-button v-show="curUser.isAdmin" :disabled="!curUser.isAdmin" :theme="'primary'" :title="'主要按钮'" class="mr10" style="margin-top:-20px;" @click="deleteGroupDialog.visible = true">
                    删除组
                </bk-button>
                <bk-dialog v-model="deleteGroupDialog.visible" theme="primary" class="delete-group-dialog" :show-footer="false">

                    <bk-form label-width="80">
                        <bk-form-item style="margin-left:15px;">
                            确认删除{{curGroup.name}}吗？
                        </bk-form-item>

                        <bk-form-item>
                            <bk-button style="margin-left: 20px;margin-right: 20px;" theme="primary" title="提交" @click.stop.prevent="deleteGroup">提交</bk-button>
                            <bk-button ext-cls="mr5" @click="deleteGroupDialog.visible = false" theme="default" title="取消">取消</bk-button>
                        </bk-form-item>
                    </bk-form>
                </bk-dialog>
                <bk-button :theme="'primary'" :title="'主要按钮'" style="margin-top:-20px;" class="mr10" @click="showApplyForGroup()">
                    申请入组
                </bk-button>
                <bk-dialog v-model="applyForGroup.dialogVisible" theme="primary" class="apply-join-club-dialog" :show-footer="false">
                    <bk-form label-width="80">
                        <bk-form-item label="组" required="true">
                            <bk-select v-model="applyForGroup.groupId" :loading="availableGroupsIsLoding" style="width: 250px;"
                                searchable>
                                <bk-option v-for="group in availableApplyGroups"
                                    :key="group.id"
                                    :id="group.id"
                                    :name="group.name">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button style="margin-left: 20px;margin-right: 40px;" theme="primary" :disabled="applyForGroup.groupId === ''" title="提交" @click.stop.prevent="doApplyforGroup()">提交</bk-button>
                            <bk-button ext-cls="mr5" @click="applyForGroup.dialogVisible = false" theme="default" title="取消">取消</bk-button>
                        </bk-form-item>
                    </bk-form>
                </bk-dialog>
                <div style="height:30px;margin-top:6px;margin-left:18px;">管理员：<span v-for="admin in curGroup.admin_list" :key="admin.id">{{admin.username}}({{admin.name}}); </span></div>
                <div style="height:30px;margin-top:6px;margin-left:18px;">创建人：<span v-if="curGroupId !== null ">{{curGroup.create_by}}({{curGroup.create_name}})</span></div>
                <div style="height:30px;margin-top:6px;margin-left:18px;">创建时间：{{curGroup.create_time}}</div>
            </div>
            <div class="line-container group-users">
                <bk-card title="组内成员">
                    <bk-link v-show="curUser.isAdmin" :disabled="!curUser.isAdmin" theme="primary" style="" @click="clickAddUser">+新增成员</bk-link>
                    <bk-input :clearable="true" v-model="searchForm.UserName" style="margin-left: 20px;width: 400px;display: inline-block;" placeholder="通过姓名搜索组内成员，可输入多个查询姓名，用空格分隔" :left-icon="'bk-icon icon-search'" @left-icon-click="searchUser"></bk-input>
                    <bk-dialog v-model="addUserDialog.visible" theme="primary" title="添加成员" class="add-group-dialog" :show-footer="false">
                        <bk-form label-width="120">
                            <bk-form-item label="成员" required="true">
                                <bk-select :disabled="false" v-model="addUserForm.id" style="width: 250px;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    searchable>
                                    <bk-option v-for="option in bkUsers"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.username + '(' + option.display_name + ')'">
                                    </bk-option>
                                </bk-select>
                            </bk-form-item>
                            <bk-form-item>
                                <bk-button style="margin-left: 20px;margin-right: 40px;" theme="primary" title="提交" @click.stop.prevent="addUser">提交</bk-button>
                                <bk-button ext-cls="mr5" @click="addUserDialog.visible = false" theme="default" title="取消">取消</bk-button>
                            </bk-form-item>
                        </bk-form>
                    </bk-dialog>
                    <bk-table style="margin-top: 15px;"
                        height="212px"
                        :data="groupUsers"
                        :size="size"
                        :pagination="pagination"
                        :virtual-render="true"
                        @row-mouse-enter="handleRowMouseEnter"
                        @row-mouse-leave="handleRowMouseLeave"
                        @page-change="handlePageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column type="index" label="序列" width="100"></bk-table-column>
                        <bk-table-column label="用户名" prop="username"></bk-table-column>
                        <bk-table-column label="姓名" prop="name"></bk-table-column>
                        <bk-table-column label="电话" prop="phone"></bk-table-column>
                        <bk-table-column label="邮箱" prop="email"></bk-table-column>
                        <bk-table-column label="操作" width="100px">
                            <template slot-scope="props">
                                <bk-button v-show="curUser.isAdmin " class="mr10" :disabled="curGroup.admin.indexOf(props.row.username) !== -1" theme="primary" text @click="removeUser(props.row)">移除</bk-button>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </bk-card>
            </div>

        </div>
    </div>
</template>

<script>
    import { bkSelect, bkOption, bkInput } from 'bk-magic-vue'
    export default {
        name: '',
        components: {
            bkSelect,
            bkOption,
            bkInput
        },
        data () {
            return {
                // 通过姓名搜索用户
                searchForm: {
                    UserName: ''
                },
                searchResult: '',
                // 用户信息
                curUser: {
                    isAdmin: false,
                    info: {
                        id: '',
                        username: ''
                    }
                },
                // 用户所有组信息
                groupsData: [],
                // 当前组信息
                curGroupId: null,
                curGroup: {
                    id: '',
                    name: '',
                    admin: '',
                    admin_list: [],
                    create_by: '',
                    create_name: '',
                    create_time: ''
                },
                // 所有蓝鲸用户
                bkUsers: [],
                // 添加组dialog样式
                addGroupDialog: {
                    visible: false
                },
                // 添加组的请求数据
                addGroupData: {
                    // 被选择的管理员id
                    adminIds: [],
                    // 向后端提交的组信息
                    formData: {
                        name: '',
                        admin: []
                    }
                },
                editGroupDialog: {
                    visible: false
                },
                // 添加组的请求数据
                editGroupData: {
                    // 被选择的管理员id
                    adminIds: [],
                    // 向后端提交的组信息
                    formData: {
                        name: '',
                        admin: []
                    }
                },
                deleteGroupDialog: {
                    visible: false
                },
                availableApplyGroups: [],
                availableGroupsIsLoding: true,
                applyForGroup: {
                    dialogVisible: false,
                    groupId: ''
                },
                // 所有组内成员数据
                groupUsers: [],
                addUserDialog: {
                    visible: false
                },
                // 拉人入组参数
                addUserForm: {
                    id: '',
                    username: '',
                    name: '',
                    phone: '',
                    email: ''
                }
            }
        },
        created () {
            this.init()
        },
        mounted () {
            this.getAllBKUser()
        },
        methods: {
            handleSingle (config) {
                config.message = this.searchResult
                config.offsetY = 80
                this.$bkMessage(config)
            },
            searchUser () {
                this.$http.post('/check_user_in_group/' + this.curGroupId + '/', this.searchForm).then(res => {
                    this.searchResult = res.data
                    console.log(this.searchResult)
                    this.handleSingle({ delay: 10000 })
                })
            },
            // 请求函数
            // 获取所有蓝鲸用户
            getAllBKUser () {
                this.$http.get('/get_all_bk_users/').then(res => {
                    this.bkUsers = res.data.results
                })
            },
            // 判断用户是否是当前组的管理员
            isManager () {

            },
            // 获取组信息，并检查当前用户是否为该组管理员
            getGroupInfo (groupId) {
                this.$http.get('/get_group_info/' + groupId + '/').then(res => {
                    this.curGroup = res.data
                    // 当前用户没加入任何组的话提示
                    if (!this.groupsData || this.groupsData.length === 0) {
                        this.$bkMessage({
                            theme: 'warning',
                            message: '您还没有加入任何组'
                        })
                        return
                    }
                    // 是否为此组管理员
                    this.curUser.isAdmin = false
                    if (this.curGroup.admin.indexOf(this.curUser.info.username) !== -1) {
                        this.curUser.isAdmin = true
                    }
                    // 切换组成员信息
                    this.getGroupUsers(groupId)
                })
            },
            // 获取组内成员
            getGroupUsers (groupId) {
                if (!groupId) {
                    // 如果没有加入任何组就不执行任何操作
                    return
                }
                this.$http.get('/get_group_users/' + groupId + '/').then(res => {
                    const groupUserDate = JSON.parse(JSON.stringify(res.data))
                    groupUserDate.map((item, index) => {
                        if (this.curGroup.admin.indexOf(item.username) !== -1) {
                            groupUserDate.unshift(groupUserDate.splice(index, 1)[0])
                        }
                    })
                    this.groupUsers = groupUserDate
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
            // 前端反应操作
            // 切换组模板、组成员、是否管理员等信息
            changeGroup (groupId) {
                if (groupId === '' || groupId === null) {
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
                    this.groupUsers = []
                    this.curUser.isAdmin = false
                } else {
                    // 更改组信息，和当前用户是否为当前组管理员信息
                    this.getGroupInfo(groupId)
                }
            },
            // 点击添加用户
            clickAddUser () {
                this.addUserDialog.visible = true
                // 默认把蓝鲸平台第一个用户放在选项框里
                this.addUserForm.id = this.bkUsers[0].id
            },
            clickEditGroup () {
                this.editGroupDialog.visible = true
                this.editGroupData.formData.name = this.curGroup.name
                // 根据curGroup中的adminUsername获取当前组管理员id
                const adminIds = []
                const vm = this
                this.bkUsers.forEach(function (user) {
                    if (vm.curGroup.admin.indexOf(user.username) !== -1) {
                        adminIds.push(user.id)
                    }
                })
                this.editGroupData.adminIds = adminIds
            },
            showApplyForGroup () {
                this.applyForGroup.dialogVisible = true
                // 获取用户（未在、未申请）组
                this.getAvailableApplyGroups()
            },
            // 初始化
            init () {
                // 初始化用户信息
                this.$http.get('/get_user/').then((res) => {
                    this.curUser.info = res.data
                    // 初始化组
                    this.$http.get('/get_user_groups/').then((res) => {
                        // 更新组信息
                        this.groupsData = res.data
                        // 当前用户没加入任何组的话提示
                        if (!this.groupsData || this.groupsData.length === 0) {
                            this.$bkMessage({
                                theme: 'warning',
                                message: '您还没有加入任何组'
                            })
                            return
                        }
                        if (this.groupsData.length !== 0) {
                            this.curGroupId = this.groupsData[0].id
                            this.changeGroup(this.curGroupId)
                        }
                    })
                })
            },
            // 新增组
            addGroup () {
                // 添加管理员信息
                const vm = this
                const adminlist = []
                this.bkUsers.forEach(function (user) {
                    if (vm.addGroupData.adminIds.indexOf(user.id) !== -1) {
                        adminlist.push(user)
                    }
                })
                // 创建组时未选择自己
                if (this.addGroupData.adminIds.indexOf(this.curUser.info.id) === -1) {
                    // 从蓝鲸用户中拉取本用户信息
                    let flag = false
                    const vm = this
                    this.bkUsers.forEach(function (user) {
                        if (vm.curUser.info.username === user.username) {
                            adminlist.push(user)
                            flag = true
                        }
                    })
                    if (!flag) {
                        const config = {}
                        config.message = '未在蓝鲸用户平台找到登录用户信息'
                        config.offsetY = 80
                        config.theme = 'error'
                        this.$bkMessage(config)
                        return
                    }
                }
                this.addGroupData.formData.admin = adminlist
                this.$http.post('/add_group/', this.addGroupData.formData).then(res => {
                    const config = {}
                    config.offsetY = 80
                    config.message = res.message
                    if (res.result) {
                        config.theme = 'success'
                        this.$bkMessage(config)
                        // 更新用户所有的组列表,后更新当前组
                        this.$http.get('/get_user_groups/').then((res2) => {
                            this.groupsData = res2.data
                            // 切换组
                            this.curGroupId = res.data.group_id
                            this.changeGroup(this.curGroupId)
                            // dialog不可见
                            this.addGroupDialog.visible = false
                            // 将dialog内的内容清空
                            this.addGroupData.formData.name = ''
                            this.addGroupData.adminIds = []
                        })
                    } else {
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            // 编辑组
            editGroup (groupId) {
                // 设置管理员信息
                const vm = this
                const adminlist = []
                this.bkUsers.forEach(function (user) {
                    if (vm.editGroupData.adminIds.indexOf(user.id) !== -1) {
                        adminlist.push(user)
                    }
                })
                this.editGroupData.formData.admin = adminlist
                // 调用更新组信息接口
                this.$http.post('/update_group/' + groupId + '/', this.editGroupData.formData).then(res => {
                    const config = {}
                    config.offsetY = 80
                    if (res.result) {
                        config.message = res.message
                        config.theme = 'success'
                        this.$bkMessage(config)
                        // 重新获取组列表
                        this.$http.get('/get_user_groups/').then((res2) => {
                            this.groupsData = res2.data
                            this.changeGroup(groupId)
                            this.editGroupDialog.visible = false
                        })
                    } else {
                        config.message = res.message
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            // 删除组
            deleteGroup () {
                this.$http.post('/delete_group/' + this.curGroupId + '/').then(res => {
                    const config = {}
                    config.offsetY = 80
                    if (res.result) {
                        config.message = res.message
                        config.theme = 'success'
                        this.$bkMessage(config)
                        this.deleteGroupDialog.visible = false
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
                        this.groupUsers = []
                        this.curUser.isAdmin = false
                        // 更新页面全部信息
                        this.init()
                    } else {
                        config.message = res.message
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            doApplyforGroup () {
                const config = {
                    offsetY: 80
                }
                this.$http.post(
                    '/apply_for_group/',
                    {
                        group_id: this.applyForGroup.groupId
                    }
                ).then(res => {
                    config.message = res.message
                    if (res.result) {
                        // 申请成功，重新获取（未申请、未在）的组列表
                        config.theme = 'success'
                        for (const i in this.availableApplyGroups) {
                            if (this.availableApplyGroups[i].id === this.applyForGroup.groupId) {
                                this.availableApplyGroups.splice(i, 1)
                                break
                            }
                        }
                        this.applyForGroup.dialogVisible = false
                    } else {
                        config.theme = 'error'
                    }
                    this.$bkMessage(config)
                })
            },
            // 新增成员
            addUser () {
                const vm = this
                this.bkUsers.forEach(function (user) {
                    if (user.id === vm.addUserForm.id) {
                        vm.addUserForm = user
                    }
                })
                this.$http.post('/add_user/' + this.curGroup.id + '/', this.addUserForm).then(res => {
                    const config = {}
                    config.offsetY = 80
                    config.message = res.message
                    if (res.result) {
                        this.addUserDialog.visible = false
                        config.theme = 'success'
                        this.$bkMessage(config)
                        // 将提交的表单清空，因为当前（刚打开时的第一个元素）和它关联
                        this.addUserForm = {}
                        // 更新组-用户信息
                        this.getGroupUsers(this.curGroup.id)
                    } else {
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            // 将用户从组中移除
            removeUser (row) {
                // 检验删除的是否是管理员
                if (this.curGroup.admin.indexOf(row.username) !== -1) {
                    const config = {}
                    config.offsetY = 80
                    config.message = '不可移除管理员，可通过编辑组信息修改'
                    config.theme = 'error'
                    this.$bkMessage(config)
                } else {
                    // props.row是当前行的遍历元素的全部信息=该行user
                    const deletForm = { 'user_id': row.id }
                    // 将用户从组里移除
                    this.$http.post('/exit_group/' + this.curGroup.id + '/', deletForm).then(res => {
                        const config = {}
                        config.offsetY = 80
                        config.message = res.message
                        if (res.result) {
                            this.getGroupUsers(this.curGroup.id)
                            config.theme = 'success'
                            this.$bkMessage(config)
                        } else {
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
    .body{
        border: 2px solid #EAEBF0 ;
        /* border-radius: 4px; */
        margin:0px 100px;
    }
    .line-container {
        margin: 20px 50px 0px 50px;
        padding-bottom: 10px;

    }
    .line-container .container-label{
        font-size: 22px;
        font-weight: 700;
    }
    .add-group-dialog /deep/ .bk-dialog-wrapper .bk-dialog .bk-dialog-content{
        width: 480px !important;
    }
    .add-group-dialog /deep/ .bk-dialog-body .bk-form-content{
        margin-left: 120px !important;
        width: 250px;
    }
    .line-container  /deep/ .bk-card .bk-card-body {
        padding-top: 10px !important;
        visibility:hidden;
        visibility:visible;
    }
    .input-demo {
        width: 500px;
    }
</style>
