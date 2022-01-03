// 判断当前用户是不是管理员
export const isAdmin = function (myUsername, adminName) {
    return adminName.includes(myUsername)
}
