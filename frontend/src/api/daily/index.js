import http from '../index.js'

// 根据日期和小组 获得当前组所有成员的日报
export function getDaily (curGroupId, curDate, curUserId, limit, curPage) {
    return new Promise((resolve, reject) => {
        http.get('/report_filter/' + curGroupId + '/?date=' + curDate + '&member_id=' + curUserId + '&size=' + limit + '&page=' + curPage).then(res => {
            resolve(res)
        })
    })
}

// 获得优秀日报
export function getGoodDaily (curGroupId, selectType, curPage, limit, year, month) {
    return new Promise((resolve, reject) => {
        http.get('/get_prefect_dailys/' + curGroupId
                    + '/?select_type=' + selectType
                    + '&page=' + curPage
                    + '&size=' + limit
                    + '&year=' + year
                    + '&month=' + month
        ).then(res => {
            resolve(res)
        })
    })
}

// 把日报设置为优秀日报
export function setGoodDaily (curGroupId, dailyId) {
    return new Promise((resolve, reject) => {
        http.patch(`/update_daily_perfect_status/${curGroupId}/${dailyId}/`).then(res => {
            resolve(res)
        })
    })
}

// 获得用户日报的填写情况(日期 哪些日期写了哪些日期没写)
export function getReportsDates () {
    return new Promise((resolve, reject) => {
        http.get(`/get_reports_dates/`).then(res => {
            resolve(res)
        })
    })
}

// 用户昨天日报的填写情况
export function getYesterday () {
    return new Promise((resolve, reject) => {
        http.get(`/check_yesterday_daliy/`).then(res => {
            resolve(res)
        })
    })
}

// 获得自己指定日期的日报
export function getAppointDaily (formatDate) {
    return new Promise((resolve, reject) => {
        http.get(`/daily_report/?date=${formatDate}`).then(res => {
            resolve(res)
        })
    })
}

// 添加或修改日报
export function setUpdateDaily (newPostDaily) {
    return new Promise((resolve, reject) => {
        http.post(`/daily_report/`, newPostDaily).then(res => {
            resolve(res)
        })
    })
}

// 查询未请假成员和请假成员信息
export function selectPerMsg (groupId, todayDate, sign) {
    return new Promise((resolve, reject) => {
        http.get(`/display_personnel_information/${groupId}/?date=${todayDate}&sign=${sign}`).then(res => {
            resolve(res)
        })
    })
}

// 组员申请请假
export function applyRest (params) {
    return new Promise((resolve, reject) => {
        http.post(`/add_off_info/`, params).then(res => {
            resolve(res)
        })
    })
}

// 撤回请假申请
export function removeOff (groupId, offdayId) {
    return new Promise((resolve, reject) => {
        http.delete('/remove_off/' + groupId + '/' + offdayId + '/').then(res => {
            resolve(res)
        })
    })
}

// 评价组员日报
export function evaluateDaily (params) {
    return new Promise((resolve, reject) => {
        http.post('/evaluate_daily/', params).then(res => {
            resolve(res)
        })
    })
}

// 删除评论
export function deleteDaily (groupid, dailyid) {
    return new Promise((resolve, reject) => {
        http.delete(`/delete_evaluate_daily/${groupid}/${dailyid}/`).then(res => {
            resolve(res)
        })
    })
}

// 修改评价
export function updateEvaluateDaily (groupid, dailyid, params) {
    return new Promise((resolve, reject) => {
        http.post(`/update_evaluate_daily/${groupid}/${dailyid}/`, params).then(res => {
            resolve(res)
        })
    })
}
