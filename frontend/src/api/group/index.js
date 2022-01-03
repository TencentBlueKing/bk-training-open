import http from '../index.js'

// 获取有权限管理的所有组
export function getAlljurGroups (params) {
    return new Promise((resolve, reject) => {
        http.get('/list_admin_group/').then(res => {
            resolve(res)
        })
    })
}

// 获得全部组
export function getallGroups (params) {
    return new Promise((resolve, reject) => {
        http.get('/get_user_groups/').then(res => {
            resolve(res)
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
