export const timeValidator = (timestamp:  string | undefined): string=>{
    console.log("LOOOTTTT.....")
    if (!timestamp) {
        console.warn('Empty timestamp provided to formatTime');
        return 'No date available';
    }

    try {
        let date: Date;

        if (/^\d+$/.test(timestamp)) {
            date = new Date(parseInt(timestamp) * 1000);
        } else if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(timestamp)) {
            date = new Date(timestamp);
        } else if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(timestamp)) {
            date = new Date(timestamp.replace(' ', 'T'));
        } else {
            date = new Date(timestamp);
        }

        if (isNaN(date.getTime())) {
            console.error('Invalid date format:', timestamp);
            return 'Invalid date format';
        }

        return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')} ${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')} UTC`;
    } catch (error) {
        console.error('Error formatting time:', error, 'timestamp:', timestamp);
        return 'Error formatting time';
    }
}
