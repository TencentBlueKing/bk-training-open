import http from '../index.js'

// 获取用户当前信息
export function getUser (params) {
    return new Promise((resolve, reject) => {
        http.get('/get_user/').then(res => {
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
