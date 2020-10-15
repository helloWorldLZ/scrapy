price = 2		#	单注价格
bonus = 5		#	中奖金额
costs = []		#	总成本

for i in range(20):
	current_costs = sum(costs)

	times = 1		#	买多少注
	while True:
		cost = times * price		#	本次购买总金额
		reward = times * bonus		#	本次中奖总金额

		costs_total = current_costs + cost 		#	总成本
		if costs_total < reward:
			costs.append(cost)

			print(i + 1, '='*10, times, '='*10, cost, '='*10, reward, '='*10, costs_total)
			break

		times += 1
