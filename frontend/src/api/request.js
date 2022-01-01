import http from './index.js'
// 获取有权限管理的所有组
export function getAlljurGroups (params) {
    return new Promise((resolve, reject) => {
        http.get('/list_admin_group/').then(res => {
            resolve(res)
        })
    })
}

// 获取用户当前信息
export function getUser (params) {
    return new Promise((resolve, reject) => {
        http.get('/get_user/').then(res => {
            // 等待优化 做缓存
            resolve(res)
        })
    })
}

// 获取所有蓝鲸用户信息
export function getAllUsers (params) {
    return new Promise((resolve, reject) => {
        http.get('/get_all_bk_users/').then(res => {
            resolve(res.data.results)
        })
    })
}

// 获取组信息，并检查当前用户是否为该组管理员
export function getGroupInfo (groupId) {
    return new Promise((resolve, reject) => {
        http.get(`/get_group_info/${groupId}/`).then(res => {
            resolve(res)
        })
    })
}

// 添加一个新组
export function addGroup (option) {
    return new Promise((resolve, reject) => {
        http.post(`/add_group/`, option).then(res => {
            resolve(res)
        })
    })
}

// 获取没加入的组
export function getNotJoinGroup () {
    return new Promise((resolve, reject) => {
        http.post(`/get_available_apply_groups/`).then(res => {
            // is_available 为0是可用
            resolve(res.data.filter(item => {
                return item.is_available === 1
            }))
        })
    })
}

// 申请入组
export function ApplyJoinGroup (option) {
    return new Promise((resolve, reject) => {
        http.post(`/apply_for_group/`, option).then(res => {
            resolve(res)
        })
    })
}

// 修改组信息
export function updateGroup (groupId, option) {
    return new Promise((resolve, reject) => {
        http.post(`/update_group/${groupId}/`, option).then(res => {
            resolve(res)
        }).catch(err => {
            console.log(err)
        })
    })
}

// 删除组
export function deleteGroup (curGroupId) {
    return new Promise((resolve, reject) => {
        http.post('/delete_group/' + curGroupId + '/').then(res => {
            resolve(res)
        })
    })
}

// 获得组成员
export function getGroupUsers (curGroupId) {
    return new Promise((resolve, reject) => {
        http.get('/get_group_users/' + curGroupId + '/').then(res => {
            resolve(res)
        })
    })
}

// 新增成员
export function addGroupUsers (curGroupId, newUserIds) {
    return new Promise((resolve, reject) => {
        http.post('/add_user/' + curGroupId + '/', { 'new_user_ids': newUserIds }).then(res => {
            resolve(res)
        })
    })
}

// 删除指定用户
export function deleteGroupUsers (curGroupId, deleteForm) {
    return new Promise((resolve, reject) => {
        http.post('/exit_group/' + curGroupId + '/', deleteForm).then(res => {
            resolve(res)
        })
    })
}
