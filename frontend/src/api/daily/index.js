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
