<script setup>
import { createResource } from 'frappe-ui';

const props = defineProps({
	payoutOrderName: {
		type: String,
		required: true
	}
});

const payout = createResource({
	url: 'press.api.marketplace.get_payout_details',
	auto: true,
	params: {
		name: props.payoutOrderName
	}
});
</script>
<template>
	<div>
		<Button v-if="payout.loading" :loading="true">{{ $t('Loading') }}</Button>

		<div v-if="payout.data">
			<table class="text w-full text-sm">
				<thead>
					<tr class="text-gray-600">
						<th class="border-b py-3 pr-2 text-left font-normal">
							{{ $t('Description') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
						>
							{{ $t('Rate') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
						>
							{{ $t('Total_Amount') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
						>
							{{ $t('Fee') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
						>
							{{ $t('Commission') }}
						</th>
						<th class="border-b py-3 pr-2 text-right font-normal">
							{{ $t('Net_Amount') }}
						</th>
					</tr>
				</thead>

				<tbody>
					<tr v-for="(row, i) in payout.data.vnd_items" :key="row.idx">
						<td class="border-b py-3 pr-2">
							{{ row.description || row.document_name }} -
							<strong class="font-semibold">{{ row.site }}</strong>
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ row.rate }} x {{ row.quantity }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ row.total_amount }} VND
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ round(row.gateway_fee, 2) }} VND
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ round(row.commission, 2) }} VND
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ round(row.net_amount, 2) }} VND
						</td>
					</tr>
				</tbody>

				<tbody>
					<tr v-for="(row, i) in payout.data.usd_items" :key="row.idx">
						<td class="border-b py-3 pr-2">
							{{ row.description || row.document_name }} -
							<strong class="font-semibold">{{ row.site }}</strong>
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ row.rate }} x {{ row.quantity }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ row.total_amount }} VND
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ round(row.gateway_fee, 2) }} VND
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ round(row.commission, 2) }} VND
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ round(row.net_amount, 2) }} VND
						</td>
					</tr>
				</tbody>

				<tfoot>
					<tr>
						<td></td>
						<td></td>
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">{{ $t('Grand_Total') }}</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							<!-- ${{ round(payout.data.net_total_usd, 2) }} + ₹{{
								round(payout.data.net_total_inr, 2)
							}} -->
							{{ round(payout.data.net_total_vnd, 0) }} VND
						</td>
					</tr>
				</tfoot>

				<tbody>
					<tr v-for="(row, i) in payout.data.inr_items" :key="row.idx">
						<td class="border-b py-3 pr-2">
							{{ row.description || row.document_name }} -
							<strong class="font-semibold">{{ row.site }}</strong>
						</td>
						<td class="border-b py-3 pr-2 text-right">
							₹{{ row.rate }} x {{ row.quantity }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							₹{{ round(row.total_amount, 2) }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							₹{{ round(row.gateway_fee, 2) }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							₹{{ round(row.commission, 2) }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							₹{{ round(row.net_amount, 2) }}
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<ErrorMessage :message="payout.error" />
	</div>
</template>
