import csv

def add_routes_id(input_file, output_file):
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    for i, row in enumerate(rows):
        row.append(i + 1)  # Add unique ID to each row

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


if __name__ == '__main__':
    add_routes_id('data/routes.dat', 'routes_id.dat')
