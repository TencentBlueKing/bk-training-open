/**
 * 判断字符串是否为合法的日期格式
 * 年月日用 - 连接 e.g. 2021-12-1
 * @param dateStr       待判断字符串
 * @returns {boolean}   是否为合法字符串
 */
const isValidDate = dateStr => {
    const dateSplit = dateStr.split('-')
    if (dateSplit.length === 3) {
        const year = +dateSplit[0]
        const month = +dateSplit[1]
        const day = +dateSplit[2]
        // 只判断是否为1900年之后的日期
        if (!(typeof year === 'number' && year >= 1900)) {
            return false
        }
        if (!(typeof month === 'number' && month >= 1 && month <= 12)) {
            return false
        }
        if (typeof day === 'number' && day >= 1 && day <= 31) {
            // 28号以内直接返回
            if (day <= 28) {
                return true
            }
            // 判断29号
            if (day === 29) {
                return month !== 2 || (year % 100 !== 0 && year % 4 === 0) || (year % 400 === 0)
            }
            // 判断30号
            if (day === 30) {
                return true
            }
            // 判断31号
            if (day === 31) {
                return [1, 3, 5, 7, 8, 10, 12].indexOf(month) > -1
            }
        }
    }
    return false
}

export {
    isValidDate
}
