// 判断当前用户是不是管理员
export const isAdmin = function (myUsername, adminName) {
    return adminName.includes(myUsername)
}

// 本地存储当前操作的组
export const setCurGroup = function (curGroup) {
    window.localStorage.setItem('curGroup', curGroup)
}

// 获得当前操作的组
export const getCurGroup = function () {
    return window.localStorage.getItem('curGroup')
}
