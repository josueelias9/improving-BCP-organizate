import { fetchTransactions } from '@/app/lib/data'
import { formatCurrency } from '@/app/lib/utils'
import { lusitana } from '@/app/ui/fonts'

function formatTransactionDate(dateString: string) {
    try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) {
            return dateString // Return original if invalid
        }
        return new Intl.DateTimeFormat('en-US', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        }).format(date)
    } catch {
        return dateString
    }
}

export default async function TransactionsTable() {
    const transactions = await fetchTransactions()

    return (
        <div className='flex w-full flex-col md:col-span-4'>
            <h2 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
                All Transactions
            </h2>
            <div className='flex grow flex-col justify-between rounded-xl bg-gray-50 p-4'>
                <div className='overflow-x-auto'>
                    <table className='min-w-full text-gray-900'>
                        <thead className='rounded-lg text-left text-sm font-normal'>
                            <tr>
                                <th scope='col' className='px-4 py-5 font-medium sm:pl-6'>
                                    ID
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Description
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Amount
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Date
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    User ID
                                </th>
                                <th scope='col' className='px-3 py-5 font-medium'>
                                    Category ID
                                </th>
                            </tr>
                        </thead>
                        <tbody className='bg-white'>
                            {transactions.map((transaction, i) => (
                                <tr
                                    key={transaction.id}
                                    className='w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg'
                                >
                                    <td className='whitespace-nowrap px-4 py-3 sm:pl-6'>
                                        <div className='truncate max-w-[100px]' title={transaction.id || 'N/A'}>
                                            {transaction.id ? `${transaction.id.substring(0, 8)}...` : 'N/A'}
                                        </div>
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        {transaction.description || 'N/A'}
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        <span
                                            className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                                                transaction.amount >= 0
                                                    ? 'bg-green-100 text-green-700'
                                                    : 'bg-red-100 text-red-700'
                                            }`}
                                        >
                                            {formatCurrency(transaction.amount || 0)}
                                        </span>
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        {formatTransactionDate(transaction.transaction_date)}
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        <div className='truncate max-w-[100px]' title={transaction.user_id || 'N/A'}>
                                            {transaction.user_id ? `${transaction.user_id.substring(0, 8)}...` : 'N/A'}
                                        </div>
                                    </td>
                                    <td className='whitespace-nowrap px-3 py-3'>
                                        <div className='truncate max-w-[100px]' title={transaction.category_id || 'N/A'}>
                                            {transaction.category_id ? `${transaction.category_id.substring(0, 8)}...` : 'N/A'}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {transactions.length === 0 && (
                        <div className='flex items-center justify-center py-10'>
                            <p className='text-gray-500'>No transactions found.</p>
                        </div>
                    )}
                </div>
                <div className='flex items-center pt-6'>
                    <p className='text-sm text-gray-500'>
                        Total: {transactions.length} transaction{transactions.length !== 1 ? 's' : ''}
                    </p>
                </div>
            </div>
        </div>
    )
}
