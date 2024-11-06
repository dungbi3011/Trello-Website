/**
 * @param {*} originalArray
 * @param {*} orderArray
 * @param {*} key = Key to order
 * @return new Ordered Array
 */

export const mapOrder = (originalArray, orderArray, key) => {
    if (!originalArray || !orderArray || !key) return []
    return [...originalArray].sort((a, b) => orderArray.indexOf(a[key]) - orderArray.indexOf(b[key]))
}